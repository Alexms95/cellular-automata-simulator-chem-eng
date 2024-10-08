from pydantic import BaseModel

class CalculationResult(BaseModel):
    result: float
