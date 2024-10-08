from pydantic import BaseModel

class SimulationResult(BaseModel):
        results: list['Simulation']
    
class Simulation(BaseModel):
    id: int
    name: str