from enum import Enum
from math import floor
import numpy as np
from schemas import SimulationBase

NL = 0
NC = 0

SurfaceTypes = Enum("SurfaceType", [("Torus", 1), ("Cylinder", 2), ("Box", 3)])

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


def calculate_cellular_automata(simulation: SimulationBase) -> np.ndarray:
    NL = simulation.gridHeight
    NC = simulation.gridLenght

    surface_type = SurfaceTypes.Box

    print(surface_type)

    print(NL, NC)

    NTOT = NC * NL

    EMPTY_FRAC = 0.31

    NEMPTY = floor(EMPTY_FRAC * NTOT)
    NCELL = NTOT - NEMPTY

    components = simulation.ingredients
    parameters = simulation.parameters

    NCOMP = len(components)

    print(NCOMP)

    NOME_COMP = [component.name for component in components]

    print(NOME_COMP)

    Ci = np.array([comp.molarFraction for comp in components])

    print(Ci)

    Ni = calculate_cell_counts(NCELL, Ci)

    print(Ni)

    # Initial matrix
    # matrix = [
    #     [0, 2, 0, 2, 1, 2, 1, 3, 1, 3],
    #     [3, 0, 0, 0, 3, 0, 3, 0, 0, 1],
    #     [0, 0, 3, 2, 1, 1, 1, 1, 1, 1],
    #     [2, 0, 0, 3, 2, 0, 3, 0, 2, 0],
    #     [0, 0, 1, 0, 2, 3, 3, 2, 2, 3],
    #     [2, 2, 3, 3, 1, 0, 2, 2, 3, 0],
    #     [2, 3, 3, 3, 1, 0, 0, 0, 1, 3],
    #     [0, 1, 1, 3, 2, 3, 1, 3, 3, 2],
    # ]
    # M = np.array(matrix)

    M = np.zeros((NL, NC), dtype=int)

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

    # Define the Von Neumann neighborhood
    NEIGH = np.array([[-1, 0], [1, 0], [0, -1], [0, 1]], dtype=int)

    # Shuffle the neighborhood
    np.random.shuffle(NEIGH)

    n_iter = simulation.iterationsNumber

    moved_components = set()

    for n in range(n_iter):
        M_new = M.copy()
        moved_components.clear()
        for i in range(NL):
            for j in range(NC):
                i_comp = M[i, j]
                if i_comp > 0 and (i, j) not in moved_components:
                    for n in range(len(NEIGH)):
                        r = i + NEIGH[n, 0]
                        c = j + NEIGH[n, 1]
                        if check_constraints(surface_type, r, c):
                            if M_new[r, c] == 0:
                                pm_component = parameters.Pm[i_comp - 1]
                                if maybe_execute(pm_component):
                                    M_new[r, c] = i_comp
                                    M_new[i, j] = 0
                                    moved_components.add((r, c))
                                    np.random.shuffle(NEIGH)
                                    break
    M = M_new.copy()
    M_new = None

    print("Final matrix:")
    show_matrix(M)
    return M


def show_matrix(M: np.ndarray):
    NL, NC = M.shape
    for i in range(NL):
        for j in range(NC):
            print(f"{M[i, j]:2d}", end=" ")
        print()
    print()

def maybe_execute(probability: float) -> bool:
    return np.random.random() < probability

def check_constraints(surface_type: SurfaceTypes, r: int, c: int) -> bool:
    if surface_type == SurfaceTypes.Box:
        return r >= 0 and r < NL and c >= 0 and c < NC
    if surface_type == SurfaceTypes.Cylinder:
        return r >= 0 and r < NL
    return True
