import json

from fastapi import HTTPException
from domain.schemas import SimulationBase, SimulationCreate
from services.cellular_automata_calculator import CellularAutomataCalculator
from utils import compress_matrix, decompress_matrix

from queries import SimulationData


class MainService:
    def __init__(self, dataAccess: SimulationData):
        self.dataAccess = dataAccess

    def get_simulations(self, db):
        return self.dataAccess.get_simulations(db)

    def get_simulation(self, simulation_id, db):
        return self.dataAccess.get_simulation(simulation_id, db)

    def create_simulation(self, newSimulation: SimulationCreate, db):
        existing_simulation = self.dataAccess.get_simulation_by_name(
            newSimulation.name, db
        )
        if existing_simulation:
            raise HTTPException(
                status_code=409,
                detail=f"A simulation named {newSimulation.name} already exists",
            )

        self.dataAccess.create_simulation(newSimulation, db)

    def update_simulation(self, simulation_id, updatedSimulation: SimulationCreate, db):
        existing_simulation = self.dataAccess.get_simulation(simulation_id, db)
        if not existing_simulation:
            raise HTTPException(status_code=400, detail="Simulation not found")

        duplicate_simulation = self.dataAccess.get_simulation_by_name_excluding_id(
            updatedSimulation.name, simulation_id, db
        )
        if duplicate_simulation:
            raise HTTPException(
                status_code=409,
                detail=f"A simulation named {updatedSimulation.name} already exists",
            )

        self.dataAccess.update_simulation(simulation_id, updatedSimulation, db)

    def delete_simulation(self, simulation_id, db):
        existing_simulation = self.dataAccess.get_simulation(simulation_id, db)
        if not existing_simulation:
            raise HTTPException(status_code=400, detail="Simulation not found")

        self.dataAccess.delete_simulation(simulation_id, db)

    async def run_simulation(self, simulation_id, db):
        simulation = self.dataAccess.get_simulation(simulation_id, db)
        if not simulation:
            raise HTTPException(status_code=400, detail="Simulation not found")

        simulation_data = SimulationBase(**simulation.__dict__)
        calculations = CellularAutomataCalculator(simulation_data)

        async for (
            current_iteration,
            total_iterations,
        ) in calculations.calculate_cellular_automata():
            yield f"data: {json.dumps({'progress': current_iteration / total_iterations})}\n\n"

        resulting_matrix, molar_fractions_table = calculations.get_results()
        compressed_matrix = compress_matrix(resulting_matrix.tolist())

        self.dataAccess.save_simulation_results(
            simulation_id, compressed_matrix, molar_fractions_table, db
        )

        yield "data: Simulation completed!\n\n"

    def get_decompressed_iterations(self, simulation_id, db):
        compressed_iterations = self.dataAccess.get_compressed_iterations(
            simulation_id, db
        )
        if compressed_iterations is None:
            return []

        return decompress_matrix(compressed_iterations)

    def get_results(self, simulation_id, db):
        name, results = self.dataAccess.get_results(simulation_id, db)
        if results is None:
            raise HTTPException(
                status_code=400, detail=f"Run the simulation {name} to generate results"
            )

        return name, results
