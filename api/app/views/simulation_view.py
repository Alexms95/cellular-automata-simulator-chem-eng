from fastapi import APIRouter, Depends

from app.controllers.simulation_controller import SimulationController
from app.schemas.simulation_schema import NewSimulation, SimulationResult

router = APIRouter()

@router.get("", response_model=SimulationResult)
def get_simulations(controller: SimulationController = Depends()):
    return controller.get_simulations()

@router.post("", response_model=None)
def create_simulation(newSimulation: NewSimulation,controller: SimulationController = Depends()):
    return controller.create_simulation(newSimulation)