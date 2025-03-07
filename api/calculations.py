from math import floor
import numpy as np
from schemas import SimulationBase

def calculate_cell_counts(total: int, percentages: list[float]) -> list[int]:
  fractional_counts = [percentage * total / 100 for percentage in percentages]
  
  rounded_counts = [floor(fraction) for fraction in fractional_counts]
  
  error = abs(sum(fractional_counts) - sum(rounded_counts))
  
  if error == 0:
    return rounded_counts

  adjustment_list = [
    {
        'index': index, 
        'difference': fraction - rounded_count
    } 
    for index, (fraction, rounded_count) in enumerate(zip(fractional_counts, rounded_counts))]
    
  adjustment_list.sort(key=lambda x: x['difference'], reverse=True)
  
  for i in range(round(error)):
    rounded_counts[adjustment_list[i]['index']] += 1
  
  return rounded_counts

def calculate_cellular_automata(simulation: SimulationBase) -> None:
    
    NL = simulation.gridHeight
    NC = simulation.gridLenght

    NTOT = NC * NL

    NCOMP = len(simulation.ingredients)
    NOME_COMP = [ingredient.name for ingredient in simulation.ingredients]

    C = np.array([37, 20, 3, 3, 3, 3])/100
