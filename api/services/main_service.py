import json

from domain.schemas import RotationInfo, SimulationBase, SimulationCreate
from fastapi import HTTPException
from queries import SimulationData
from services.cellular_automata_calculator import CellularAutomataCalculator
from services.movement_analyzer import MovementAnalyzer
from services.reaction_processor import ReactionProcessor
from services.rotation_manager import RotationManager
from services.simulation_state import SimulationState
from utils import compress_matrix, decompress_matrix, get_component_index


class MainService:
    def __init__(self, dataAccess: SimulationData):
        self.dataAccess = dataAccess

    def get_simulations(self):
        return self.dataAccess.get_simulations()

    def get_simulation(self, simulation_id):
        return self.dataAccess.get_simulation(simulation_id)

    def create_simulation(self, newSimulation: SimulationCreate):
        existing_simulation = self.dataAccess.get_simulation_by_name(newSimulation.name)
        if existing_simulation:
            raise HTTPException(
                status_code=409,
                detail=f"A simulation named {newSimulation.name} already exists",
            )

        self.dataAccess.create_simulation(newSimulation)

    def update_simulation(self, simulation_id, updatedSimulation: SimulationCreate):
        existing_simulation = self.dataAccess.get_simulation(simulation_id)
        if not existing_simulation:
            raise HTTPException(status_code=400, detail="Simulation not found")

        duplicate_simulation = self.dataAccess.get_simulation_by_name_excluding_id(
            updatedSimulation.name, simulation_id
        )
        if duplicate_simulation:
            raise HTTPException(
                status_code=409,
                detail=f"A simulation named {updatedSimulation.name} already exists",
            )

        self.dataAccess.update_simulation(simulation_id, updatedSimulation)

    def delete_simulation(self, simulation_id):
        existing_simulation = self.dataAccess.get_simulation(simulation_id)
        if not existing_simulation:
            raise HTTPException(status_code=400, detail="Simulation not found")

        self.dataAccess.delete_simulation(simulation_id)

    async def run_simulation(self, simulation_id):
        simulation_data = self.dataAccess.get_simulation(simulation_id)
        if not simulation_data:
            raise HTTPException(status_code=400, detail="Simulation not found")
        
        simulation = SimulationBase(**simulation_data._asdict())

        rotation_manager = RotationManager(simulation.rotation)

        simulation_state = SimulationState()

        movement_analyzer = MovementAnalyzer(
            simulation.rotation.component,
            rotation_manager,
            simulation.parameters,
        )

        reaction_processor = ReactionProcessor(simulation.reactions)

        calculations = CellularAutomataCalculator(
            simulation,
            movement_analyzer,
            reaction_processor,
            rotation_manager,
            simulation_state,
        )

        async for (
            current_iteration,
            total_iterations,
        ) in calculations.calculate_cellular_automata():
            yield f"data: {json.dumps({'progress': current_iteration / total_iterations})}\n\n"

        resulting_matrix, molar_fractions_table = calculations.get_results()
        
        yield "data: Calculations completed, processing results...\n\n"

        self.save_simulation_results(
            simulation_id, resulting_matrix.tolist(), molar_fractions_table
        )

        yield "data: Simulation completed!\n\n"


    def get_results(self, simulation_id):
        name, results = self.dataAccess.get_results(simulation_id)
        if results is None:
            raise HTTPException(
                status_code=400, detail=f"Run the simulation {name} to generate results"
            )

        return name, results
    

    def _setup_rotation_info(self, simulation: SimulationBase) -> RotationInfo:
        """Sets up rotation information"""
        rotation_info: RotationInfo = {"component": -1, "p_rot": 0, "states": [0]}

        if simulation.rotation.component and simulation.rotation.component != "None":

            rot_comp_index = get_component_index(simulation.rotation.component)
            rotation_info = {
                "component": rot_comp_index,
                "p_rot": simulation.rotation.Prot,
                "states": [rot_comp_index * 10 + i for i in range(1, 5)],
            }

        return rotation_info

    def save_simulation_results(
        self, simulation_id, resulting_matrix: list[list[list]], molar_fractions_table
    ):
        # Divide into chunks (1000 iterations per chunk)
        chunks = []
        for chunk_number, start in enumerate(range(0, len(resulting_matrix), 1000)):
            chunk_data = {
                "chunk_number": chunk_number,
                "data": compress_matrix(
                    resulting_matrix[start : start + 1000]
                ),
            }
            chunks.append(chunk_data)

        self.dataAccess.save_simulation_results(
            simulation_id, chunks, molar_fractions_table
        )


    def get_iterations_by_simulation(self, simulation_id: str, chunk_number: int = 0):
        return self.dataAccess.get_iterations_by_simulation(simulation_id, chunk_number)

    def get_decompressed_iterations(self, simulation_id: str, chunk_number: int = 0):
        iterations = self.get_iterations_by_simulation(simulation_id, chunk_number)
        if not iterations:
            raise HTTPException(status_code=404, detail="No iterations found for this simulation")

        decompressed_data = decompress_matrix(iterations.data)
        return decompressed_data
