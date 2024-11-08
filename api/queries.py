from fastapi import HTTPException
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
    
  def delete_simulation(self, simulation_id: str, db: Session) -> None:
    db_simulation = db.query(SimulationModel).filter(SimulationModel.id == simulation_id).first()
    if db_simulation is None:
      raise HTTPException(status_code=400, detail="Simulation not found")
    db.delete(db_simulation)
    db.commit()