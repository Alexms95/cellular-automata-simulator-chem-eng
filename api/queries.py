from sqlalchemy import select
from utils import compress_matrix, decompress_matrix
from calculations import Calculations
from fastapi import HTTPException
from models import SimulationModel
from schemas import SimulationBase, SimulationCreate
from sqlalchemy.orm import Session, load_only

SELECT_WITHOUT_ITERATIONS = select(
    SimulationModel.id,
    SimulationModel.name,
    SimulationModel.iterationsNumber,
    SimulationModel.gridLenght,
    SimulationModel.gridHeight,
    SimulationModel.ingredients,
    SimulationModel.parameters,
    SimulationModel.created_at,
    SimulationModel.updated_at,
    SimulationModel.reactions,
    SimulationModel.rotation,
)


class SimulationData:
    def get_simulations(self, db: Session) -> list[SimulationModel]:
        return db.execute(SELECT_WITHOUT_ITERATIONS).all()

    def get_simulation(self, simulation_id: str, db: Session) -> SimulationModel:
        query = select(SimulationModel).where(SimulationModel.id == simulation_id)
        db_simulation = db.execute(query).scalars().first()

        if db_simulation is None:
            raise HTTPException(status_code=400, detail="Simulation not found")

        return db_simulation

    def get_decompressed_iterations(self, simulation_id: str, db: Session) -> list[list[list[int]]]:
        query = select(SimulationModel.name, SimulationModel.iterations).where(SimulationModel.id == simulation_id)
        db_simulation = db.execute(query).first()

        if db_simulation is None:
            raise HTTPException(status_code=400, detail="Simulation not found")
        
        _, compressed_iterations = db_simulation

        if compressed_iterations is None:
            return []

        return decompress_matrix(compressed_iterations)

    def create_simulation(self, newSimulation: SimulationCreate, db: Session) -> None:
        query = SELECT_WITHOUT_ITERATIONS.where(
            SimulationModel.name == newSimulation.name
        )
        already_exists = db.execute(query).first()
        if already_exists:
            raise HTTPException(
                status_code=409,
                detail=f"A simulation named {newSimulation.name} already exists",
            )

        db_simulation = SimulationModel(**newSimulation.model_dump())

        totalCells = newSimulation.gridLenght * newSimulation.gridHeight

        ingredientCellsCount = Calculations.calculate_cell_counts(
            totalCells,
            map(lambda ingredient: ingredient.molarFraction, newSimulation.ingredients),
        )

        for i, cellsCount in enumerate(ingredientCellsCount):
            db_simulation.ingredients[i]["initialCellsCount"] = cellsCount

        db.add(db_simulation)
        db.commit()
        db.refresh(db_simulation)

    def update_simulation(
        self, simulation_id: str, updatedSimulation: SimulationCreate, db: Session
    ) -> None:
        query = (
            select(SimulationModel)
            .options(
                load_only(
                    SimulationModel.id,
                    SimulationModel.name,
                    SimulationModel.iterationsNumber,
                    SimulationModel.gridLenght,
                    SimulationModel.gridHeight,
                    SimulationModel.ingredients,
                    SimulationModel.parameters,
                    SimulationModel.created_at,
                    SimulationModel.updated_at,
                    SimulationModel.reactions,
                    SimulationModel.rotation,
                )
            )
            .where(SimulationModel.id == simulation_id)
        )
        db_simulation = db.execute(query).scalars().first()

        if db_simulation is None:
            raise HTTPException(status_code=400, detail="Simulation not found")

        query = (
            SELECT_WITHOUT_ITERATIONS
            .where(
                SimulationModel.id != simulation_id,
                SimulationModel.name == updatedSimulation.name,
            )
        )
        already_exists = db.execute(query).first()

        if already_exists:
            raise HTTPException(
                status_code=409,
                detail=f"A simulation named {updatedSimulation.name} already exists",
            )

        for key, value in updatedSimulation.model_dump(exclude_unset=True).items():
            setattr(db_simulation, key, value)

        totalCells = updatedSimulation.gridLenght * updatedSimulation.gridHeight

        ingredientCellsCount = Calculations.calculate_cell_counts(
            totalCells,
            map(
                lambda ingredient: ingredient.molarFraction,
                updatedSimulation.ingredients,
            ),
        )

        for i, cellsCount in enumerate(ingredientCellsCount):
            db_simulation.ingredients[i]["initialCellsCount"] = cellsCount

        db.commit()
        db.refresh(db_simulation)

    def delete_simulation(self, simulation_id: str, db: Session) -> None:
        query = select(SimulationModel).options(load_only(SimulationModel.id)).where(
            SimulationModel.id == simulation_id,
        )
        db_simulation = db.execute(query).scalars().first()

        if db_simulation is None:
            raise HTTPException(status_code=400, detail="Simulation not found")

        db.delete(db_simulation)
        db.commit()

    def run_simulation(self, simulation_id: str, db: Session) -> None:
        query = select(SimulationModel).options(
            load_only(
                SimulationModel.id,
                SimulationModel.name,
                SimulationModel.iterationsNumber,
                SimulationModel.gridLenght,
                SimulationModel.gridHeight,
                SimulationModel.ingredients,
                SimulationModel.parameters,
                SimulationModel.created_at,
                SimulationModel.updated_at,
                SimulationModel.reactions,
                SimulationModel.rotation,
            )
        ).where(SimulationModel.id == simulation_id)
        db_simulation = db.execute(query).scalars().first()

        if db_simulation is None:
            raise HTTPException(status_code=400, detail="Simulation not found")

        simulation = SimulationBase(**db_simulation.__dict__)

        resulting_matrix = Calculations.calculate_cellular_automata(simulation).tolist()
        db_simulation.iterations = compress_matrix(resulting_matrix)
        db.commit()
        db.refresh(db_simulation)
