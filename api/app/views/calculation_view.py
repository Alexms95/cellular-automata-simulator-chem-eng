from fastapi import APIRouter, Depends
from app.schemas.calculation_schema import CalculationInput, CalculationResult
from app.controllers.calculation_controller import CalculationController

router = APIRouter()

@router.post("/add", response_model=CalculationResult)
def add_numbers(calculation: CalculationInput, controller: CalculationController = Depends()):
    return controller.add(calculation)

@router.post("/subtract", response_model=CalculationResult)
def subtract_numbers(calculation: CalculationInput, controller: CalculationController = Depends()):
    return controller.subtract(calculation)
