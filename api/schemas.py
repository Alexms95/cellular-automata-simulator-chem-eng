from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class Ingredient(BaseModel):
  name: str
  initialNumber: int
  color: str

class PairParameter(BaseModel):
  fromIngr: str
  toIngr: str
  value: float
  
class Parameters(BaseModel):
  Pm: list[float]
  Pb: list[PairParameter]
  J: list[PairParameter]
    
class SimulationBase(BaseModel):
  name: str
  iterationsNumber: int
  gridLenght: int
  gridHeight: int
  ingredients: list[Ingredient]
  parameters: Parameters
  
class SimulationCreate(SimulationBase):
  pass

class SimulationResponse(SimulationBase):
  id: UUID
  created_at: datetime
  updated_at: datetime
  class Config:
    from_attributes = True