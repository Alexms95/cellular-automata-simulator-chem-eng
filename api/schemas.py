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
  gridSize: int
  ingredients: list[Ingredient]
  parameters: Parameters
  
class SimulationCreate(SimulationBase):
  pass

class SimulationResponse(SimulationBase):
  id: UUID
  class Config:
    from_attributes = True