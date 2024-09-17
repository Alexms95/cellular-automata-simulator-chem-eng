from pydantic import BaseModel

class CalculationInput(BaseModel):
    a: float
    b: float

class CalculationResult(BaseModel):
    result: float
