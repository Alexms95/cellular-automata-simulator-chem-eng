from fastapi import HTTPException
from models import SimulationModel
from schemas import SimulationCreate
from sqlalchemy.orm import Session

class SimulationData:
  def get_simulations(self, db: Session) -> list[SimulationModel]:
    return db.query(SimulationModel).all()
    
  def create_simulation(self, newSimulation: SimulationCreate, db: Session) -> None:
    already_exists = db.query(SimulationModel).filter(SimulationModel.name == newSimulation.name).first()
    if already_exists:
      raise HTTPException(status_code=409, detail=f"A simulation named {newSimulation.name} already exists")
    db_simulation = SimulationModel(**newSimulation.model_dump())
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    
  def update_simulation(self, simulation_id: str, updatedSimulation: SimulationCreate, db: Session) -> None:
    db_simulation = db.query(SimulationModel).filter(SimulationModel.id == simulation_id).first()
    
    if db_simulation is None:
      raise HTTPException(status_code=400, detail="Simulation not found")
    already_exists = db.query(SimulationModel).filter(SimulationModel.name == updatedSimulation.name).first()
    
    if already_exists:
      raise HTTPException(status_code=409, detail=f"A simulation named {updatedSimulation.name} already exists")
    
    for key, value in updatedSimulation.model_dump(exclude_unset=True).items():
        setattr(db_simulation, key, value)
        
    db.commit()
    db.refresh(db_simulation)
    
  def delete_simulation(self, simulation_id: str, db: Session) -> None:
    db_simulation = db.query(SimulationModel).filter(SimulationModel.id == simulation_id).first()
    if db_simulation is None:
      raise HTTPException(status_code=400, detail="Simulation not found")
    db.delete(db_simulation)
    db.commit()