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
        {"index": index, "difference": fraction - rounded_count}
        for index, (fraction, rounded_count) in enumerate(
            zip(fractional_counts, rounded_counts)
        )
    ]

    adjustment_list.sort(key=lambda x: x["difference"], reverse=True)

    for i in range(round(error)):
        rounded_counts[adjustment_list[i]["index"]] += 1

    return rounded_counts


def calculate_cellular_automata(simulation: SimulationBase) -> np.matrix:

    NL = simulation.gridHeight
    NC = simulation.gridLenght

    print(NL, NC)

    NTOT = NC * NL

    EMPTY_FRAC = 0.31

    NEMPTY = floor(EMPTY_FRAC * NTOT)
    NCELL = NTOT - NEMPTY

    ingredients = simulation.ingredients

    NCOMP = len(ingredients)

    print(NCOMP)

    NOME_COMP = [ingredient.name for ingredient in ingredients]

    print(NOME_COMP)

    Ci = np.array([ing.molarFraction for ing in ingredients])

    print(Ci)

    Ni = calculate_cell_counts(NCELL, Ci)

    print(Ni)

    # Initial matrix
    M = np.matrix(np.zeros((NL, NC)), dtype=int)
    # Randomly distribute the components in the matrix
    for i in range(NCOMP):
        for j in range(Ni[i]):
            while True:
                r = np.random.randint(0, NL)
                c = np.random.randint(0, NC)
                if M[r, c] == 0:
                    M[r, c] = i + 1
                    break
                
    # Show the matrix formatting the output as a table
    print("Initial matrix:")
    show_matrix(M)
  
    # Define the neighborhood
    NEIGH = [[-1, 0], [1, 0], [0, -1], [0, 1]]

    # Define the number of iterations
    n_iter = simulation.iterationsNumber

    return M

def show_matrix(M):
    NL, NC = M.shape
    for i in range(NL):
        for j in range(NC):
            print(f"{M[i, j]:2d}", end=" ")
        print()
    print()

    
