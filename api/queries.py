from domain.models import IterationsModel, SimulationModel
from domain.schemas import SimulationCreate
from sqlalchemy import select
from sqlalchemy.orm import Session

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
    def __init__(self, db: Session):
        self.db = db

    def get_simulations(self):
        return self.db.execute(SELECT_WITHOUT_ITERATIONS).all()

    def get_simulation(self, simulation_id: str):
        query = SELECT_WITHOUT_ITERATIONS.where(SimulationModel.id == simulation_id)
        return self.db.execute(query).first()

    def get_simulation_by_name(self, name: str):
        query = SELECT_WITHOUT_ITERATIONS.where(SimulationModel.name == name)
        return self.db.execute(query).first()

    def get_simulation_by_name_excluding_id(self, name: str, simulation_id: str):
        query = SELECT_WITHOUT_ITERATIONS.where(
            SimulationModel.name == name, SimulationModel.id != simulation_id
        )
        return self.db.execute(query).first()

    def create_simulation(self, newSimulation: SimulationCreate):
        db_simulation = SimulationModel(**newSimulation.model_dump())
        self.db.add(db_simulation)
        self.db.commit()
        self.db.refresh(db_simulation)

    def update_simulation(
        self, simulation_id: str, updatedSimulation: SimulationCreate
    ):
        query = select(SimulationModel).where(SimulationModel.id == simulation_id)
        db_simulation = self.db.execute(query).scalars().first()

        for key, value in updatedSimulation.model_dump(exclude_unset=True).items():
            setattr(db_simulation, key, value)

        self.db.commit()
        self.db.refresh(db_simulation)

    def delete_simulation(self, simulation_id: str):
        query = select(SimulationModel).where(SimulationModel.id == simulation_id)
        db_simulation = self.db.execute(query).scalars().first()
        self.db.delete(db_simulation)
        self.db.commit()

    def save_simulation_results(
        self, simulation_id: str, chunks: list[dict], molar_fractions_table: list
    ):
        query = select(SimulationModel).where(SimulationModel.id == simulation_id)
        db_simulation = self.db.execute(query).scalars().first()

        # Clear existing iterations for the simulation
        self.db.query(IterationsModel).filter(
            IterationsModel.simulation_id == simulation_id
        ).delete()

        for chunk_data in chunks:
            iteration_entry = IterationsModel(
                simulation_id=simulation_id,
                chunk_number=chunk_data["chunk_number"],
                data=chunk_data["data"],
            )
            self.db.add(iteration_entry)

        db_simulation.results = molar_fractions_table

        self.db.commit()
        self.db.refresh(db_simulation)

    def get_results(self, simulation_id: str):
        query = select(SimulationModel.name, SimulationModel.results).where(
            SimulationModel.id == simulation_id
        )
        return self.db.execute(query).first()

    def get_iterations_by_simulation(self, simulation_id: str, chunk_number: int = 0):
        query = select(IterationsModel).where(
            IterationsModel.simulation_id == simulation_id,
            IterationsModel.chunk_number == chunk_number,
        )
        return self.db.execute(query).scalars().first()
