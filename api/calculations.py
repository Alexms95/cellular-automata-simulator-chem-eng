from enum import Enum
from math import floor

import numpy as np
from utils import get_component_index
from schemas import PairParameter, SimulationBase

SurfaceTypes = Enum("SurfaceType", [("Torus", 1), ("Cylinder", 2), ("Box", 3)])


class Calculations:
    NL = 0
    NC = 0

    @staticmethod
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

    @staticmethod
    def calculate_cellular_automata(simulation: SimulationBase) -> np.ndarray:
        Calculations.NL = simulation.gridHeight
        Calculations.NC = simulation.gridLenght

        NL = Calculations.NL
        NC = Calculations.NC

        surface_type = SurfaceTypes.Box

        NTOT = NC * NL

        EMPTY_FRAC = 0.31  # Fraction of empty cells

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
        Ni = Calculations.calculate_cell_counts(NCELL, Ci)

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
        Calculations.show_matrix(M)

        # Define the Von Neumann neighborhood
        von_neumann_neigh = np.array([[-1, 0], [1, 0], [0, -1], [0, 1]], dtype=int)

        n_iter = simulation.iterationsNumber

        pbs = Calculations.calculate_pbs(parameters.J)

        moved_components = set()

        random_generator = np.random.default_rng()

        for n in range(n_iter):
            M_new = M.copy()
            moved_components.clear()
            for i in range(NL):
                for j in range(NC):
                    current_position = (i, j)
                    i_comp = M[i, j]
                    if i_comp > 0 and current_position not in moved_components:
                        inner_neighbors_position = von_neumann_neigh + current_position
                        outer_neighbors_position = (
                            2 * von_neumann_neigh + current_position
                        )

                        occuped_inner_neighbors = []

                        J_neighbors = []
                        j_components = 0

                        # New version
                        for i_p in range(len(inner_neighbors_position)):
                            row_index, column_index = inner_neighbors_position[i_p]
                            if Calculations.check_constraints(
                                surface_type, row_index, column_index
                            ):
                                if M[row_index, column_index] == 0:
                                    o_row, o_column = outer_neighbors_position[i_p]
                                    if not Calculations.check_constraints(
                                        surface_type, o_row, o_column
                                    ):
                                        J_neighbors.append((i_p, 0))
                                        continue
                                    outer_component = M[o_row, o_column]
                                    if outer_component != 0:
                                        # Search in the list for the probability J of the component
                                        j_components = next(
                                            (
                                                j.value
                                                for j in parameters.J
                                                if (
                                                    get_component_index(j.fromIngr)
                                                    == i_comp
                                                    and get_component_index(j.toIngr)
                                                    == outer_component
                                                )
                                                or (
                                                    get_component_index(j.fromIngr)
                                                    == outer_component
                                                    and get_component_index(j.toIngr)
                                                    == i_comp
                                                )
                                            )
                                        )
                                    J_neighbors.append((i_p, j_components))
                                else:
                                    occuped_inner_neighbors.append(
                                        (row_index, column_index)
                                    )

                        if len(J_neighbors) == 0:
                            continue

                        J_max = max(J_neighbors, key=lambda x: x[1])

                        if J_max[1] < 1 and J_max[1] != 0:
                            continue

                        if J_max[1] == 0:
                            # If J_max is 0, all empty neighbors have J = 0 and are equal in terms of "afinity", so pick one randomly
                            J_max = random_generator.choice(J_neighbors)
                        else:
                            # If J_max is not 0, pick the empty neighbor with the highest J value
                            J_neigh_max = list(
                                filter(lambda x: x[1] == J_max[1], J_neighbors)
                            )
                            if len(J_neigh_max) > 1:
                                # If there are more than one neighbor with the same J_max value, pick one randomly
                                J_max = random_generator.choice(J_neigh_max)

                        pbs_product = 1

                        if len(occuped_inner_neighbors) > 0:
                            pb_inner_components = []
                            for comp_position in occuped_inner_neighbors:
                                row, column = comp_position
                                comp_index = M[row, column]
                                pair_list = [comp_index, i_comp]
                                pair_list.sort()
                                pair = tuple(pair_list)
                                pb = pbs[pair]
                                pb_inner_components.append(pb)
                            pbs_product = np.array(pb_inner_components).prod()

                        pm_total_component = parameters.Pm[i_comp - 1] * pbs_product

                        if Calculations.maybe_execute(pm_total_component):
                            # Move the component to the empty neighbor with the highest J value
                            row_move, column_move = inner_neighbors_position[int(J_max[0])]
                            M_new[row_move, column_move] = i_comp
                            M_new[i, j] = 0
                            moved_components.add((row_move, column_move))
                            break
        M = M_new.copy()
        M_new = None

        print("Final matrix:")
        Calculations.show_matrix(M)
        return M

    @staticmethod
    def show_matrix(M: np.ndarray):
        NL, NC = M.shape
        for i in range(NL):
            for j in range(NC):
                print(f"{M[i, j]:2d}", end=" ")
            print()
        print()

    @staticmethod
    def maybe_execute(probability: float) -> bool:
        return np.random.random() < probability

    @staticmethod
    def check_constraints(surface_type: SurfaceTypes, r: int, c: int) -> bool:
        if surface_type == SurfaceTypes.Box:
            return r >= 0 and r < Calculations.NL and c >= 0 and c < Calculations.NC
        if surface_type == SurfaceTypes.Cylinder:
            return r >= 0 and r < Calculations.NL
        return True

    @staticmethod
    def calculate_pbs(js: list[PairParameter]):
        return {
            (get_component_index(j.fromIngr), get_component_index(j.toIngr)): (3 / 2)
            / (j.value + (3 / 2))
            for j in js
        }
