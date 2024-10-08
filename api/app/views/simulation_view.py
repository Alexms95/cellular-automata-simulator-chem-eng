from fastapi import APIRouter, Depends

from app.controllers.simulation_controller import SimulationController
from app.schemas.simulation_schema import SimulationResult

router = APIRouter()

@router.get("", response_model=SimulationResult)
def get_simulations(controller: SimulationController = Depends()):
    return controller.get_simulations()
