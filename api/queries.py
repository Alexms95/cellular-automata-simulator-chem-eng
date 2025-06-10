from domain.schemas import SimulationCreate
from domain.models import SimulationModel
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
    def get_simulations(self, db: Session):
        return db.execute(SELECT_WITHOUT_ITERATIONS).all()

    def get_simulation(self, simulation_id: str, db: Session):
        query = select(SimulationModel).where(SimulationModel.id == simulation_id)
        return db.execute(query).scalars().first()

    def get_simulation_by_name(self, name: str, db: Session):
        query = SELECT_WITHOUT_ITERATIONS.where(SimulationModel.name == name)
        return db.execute(query).first()

    def get_simulation_by_name_excluding_id(
        self, name: str, simulation_id: str, db: Session
    ):
        query = SELECT_WITHOUT_ITERATIONS.where(
            SimulationModel.name == name, SimulationModel.id != simulation_id
        )
        return db.execute(query).first()

    def get_compressed_iterations(self, simulation_id: str, db: Session):
        query = select(SimulationModel.iterations).where(
            SimulationModel.id == simulation_id
        )
        result = db.execute(query).first()
        return result[0] if result else None

    def create_simulation(self, newSimulation: SimulationCreate, db: Session):
        db_simulation = SimulationModel(**newSimulation.model_dump())
        db.add(db_simulation)
        db.commit()
        db.refresh(db_simulation)

    def update_simulation(self, simulation_id: str, updatedSimulation: SimulationCreate, db: Session):
        query = select(SimulationModel).where(SimulationModel.id == simulation_id)
        db_simulation = db.execute(query).scalars().first()

        for key, value in updatedSimulation.model_dump(exclude_unset=True).items():
            setattr(db_simulation, key, value)

        db.commit()
        db.refresh(db_simulation)

    def delete_simulation(self, simulation_id: str, db: Session):
        query = select(SimulationModel).where(SimulationModel.id == simulation_id)
        db_simulation = db.execute(query).scalars().first()
        db.delete(db_simulation)
        db.commit()

    def save_simulation_results(
        self, simulation_id: str, compressed_matrix, molar_fractions_table, db: Session
    ):
        query = select(SimulationModel).where(SimulationModel.id == simulation_id)
        db_simulation = db.execute(query).scalars().first()

        db_simulation.iterations = compressed_matrix
        db_simulation.results = molar_fractions_table

        db.commit()
        db.refresh(db_simulation)

    def get_results(self, simulation_id: str, db: Session):
        query = select(SimulationModel.name, SimulationModel.results).where(
            SimulationModel.id == simulation_id
        )
        return db.execute(query).first()
