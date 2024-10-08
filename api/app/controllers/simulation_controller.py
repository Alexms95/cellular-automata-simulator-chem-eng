from app.schemas.simulation_schema import Simulation, SimulationResult

class SimulationController:
    def get_simulations(self) -> SimulationResult:
      results = [ Simulation(id=i, name=f"Simulation {i}") for i in range(1, 6) ]
      return SimulationResult(results=results)