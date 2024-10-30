from app.schemas.simulation_schema import NewSimulation, Simulation, SimulationResult

class SimulationController:
  def get_simulations(self) -> SimulationResult:
    results = [ Simulation(id=i, name=f"Simulation {i}") for i in range(1, 6) ]
    return SimulationResult(results=results)
    
  def create_simulation(self, newSimulation: NewSimulation) -> None:
    print(f"\n\nSimulation Details:\n"
      f"  Name: {newSimulation.simulationName}\n"
      f"  Iterations: {newSimulation.iterationsNumber}\n"
      f"  Grid Dimension: {newSimulation.gridDimension}\n"
      f"  Ingredients:")
    for ingredient in newSimulation.ingredients:
      print(f"  - {ingredient.name} ({ingredient.color})")
    print("\n")