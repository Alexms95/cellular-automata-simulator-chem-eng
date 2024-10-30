from pydantic import BaseModel

class SimulationResult(BaseModel):
  results: list['Simulation']
    
class Simulation(BaseModel):
  id: int
  name: str

class Ingredient(BaseModel):
  name: str
  color: str
    
class NewSimulation(BaseModel):
  simulationName: str
  iterationsNumber: int
  gridDimension: int
  ingredients: list[Ingredient]