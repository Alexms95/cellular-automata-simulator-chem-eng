from pydantic import BaseModel

class SimulationResult(BaseModel):
  results: list['SimulationMock']
    
class SimulationMock(BaseModel):
  id: int
  name: str

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
    
class Simulation(BaseModel):
  simulationName: str
  iterationsNumber: int
  gridDimension: int
  ingredients: list[Ingredient]
  parameters: Parameters