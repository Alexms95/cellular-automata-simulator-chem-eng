from models import SimulationModel
from schemas import SimulationCreate
from sqlalchemy.orm import Session

class SimulationData:
  def get_simulations(self, db: Session) -> list[SimulationModel]:
    return db.query(SimulationModel).all()
    
  def create_simulation(self, newSimulation: SimulationCreate, db: Session) -> None:
    db_simulation = SimulationModel(**newSimulation.model_dump())
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)