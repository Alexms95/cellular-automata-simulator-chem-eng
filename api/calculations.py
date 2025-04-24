from enum import Enum
from io import StringIO
from math import floor

import numpy as np
from logger import logger
from schemas import PairParameter, SimulationBase
from utils import get_component_index

SurfaceTypes = Enum("SurfaceType", [("Torus", 1), ("Cylinder", 2), ("Box", 3)])


class Calculations:
    NL = 0
    NC = 0
    NEMPTY = 0

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

        Calculations.NEMPTY = floor(EMPTY_FRAC * NTOT)
        NCELL = NTOT - Calculations.NEMPTY

        components = simulation.ingredients
        parameters = simulation.parameters

        NCOMP = len(components)

        print(NCOMP)

        NOME_COMP = [component.name for component in components]

        print(NOME_COMP)

        Ci = np.array([comp.molarFraction for comp in components])

        print(Ci)
        Ni = Calculations.calculate_cell_counts(NCELL, Ci)

        M = np.zeros((NL, NC), dtype=np.int16)

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
        von_neumann_neigh = np.array([[-1, 0], [1, 0], [0, -1], [0, 1]], dtype=np.int16)

        n_iter = simulation.iterationsNumber

        pbs = Calculations.calculate_pbs(parameters.J)

        moved_components = set()
        reacted_components = set()
        not_reacted_components = set()

        random_generator = np.random.default_rng()

        logger.info(
            "Simulation Inputs:\n"
            f"  Grid Dimensions: Lines={NL}, Columns={NC}\n"
            f"  Number of Components: NCOMP={NCOMP}\n"
            f"  Component Names: {NOME_COMP}\n"
            f"  Molar Fractions (Ci): {Ci}\n"
            f"  Cell Counts (Ni): {Ni}\n"
            f"  Surface Type: {surface_type}\n"
            f"  Empty Cells: NEMPTY={Calculations.NEMPTY}\n"
            f"  Occupied Cells: NCELL={NCELL}\n"
            f"  Number of Iterations: n_iter={n_iter}"
        )

        iteration_log_text = StringIO()

        intermediate_pairs = []

        # Create the empty array to store the matrix at each iteration
        M_iter = np.zeros((n_iter + 1, NL, NC), dtype=np.int16)

        # Store the initial matrix in the first slice of M_iter
        M_iter[0, :, :] = M.copy()

        for n in range(1, n_iter + 1):
            moved_components.clear()
            reacted_components.clear()
            not_reacted_components.clear()
            for i in range(NL):
                for j in range(NC):
                    current_position = (i, j)
                    i_comp = M[i, j]
                    inner_neighbors_position = von_neumann_neigh + current_position
                    outer_neighbors_position = 2 * von_neumann_neigh + current_position

                    # Initialize variables used in the calculations
                    possible_reactions = []
                    true_sum = 0
                    false_sum = 0
                    total_sum = 0
                    normalized_probabilities = []
                    chosen_reaction = None
                    J_neighbors = []
                    occupied_inner_neighbors = []
                    J_max = None
                    J_0 = []
                    J_neigh_max = []
                    pb_inner_components = []
                    pm_total_component = 0

                    if i_comp > 0:
                        if current_position not in reacted_components:
                            try:
                                # Scan all the neighbors of the component to get all reaction pairs
                                possible_reactions = []
                                poss_reac_index = 0
                                for inner_neighbor_pos in inner_neighbors_position:
                                    row_index, column_index = inner_neighbor_pos
                                    if Calculations.check_constraints(
                                        surface_type, row_index, column_index
                                    ):
                                        inner_pos_tuple = (row_index, column_index)
                                        inner_comp = M[row_index, column_index]
                                        positions_pair = (
                                            current_position,
                                            inner_pos_tuple,
                                        )
                                        reversed_positions_pair = (
                                            inner_pos_tuple,
                                            current_position,
                                        )
                                        # Skip empty cells, the same component, already not reacted components, already reacted components in the neighborhood, and moved components in the neighborhood
                                        if (
                                            inner_comp == 0
                                            or inner_comp == i_comp
                                            or positions_pair in not_reacted_components
                                            or reversed_positions_pair
                                            in not_reacted_components
                                            or inner_pos_tuple in reacted_components
                                            # TODO: maybe this condition is not needed
                                            or inner_pos_tuple in moved_components
                                            # Exclude the case where both components are intermediates but are not a pair (avoid single intermediates in the grid)
                                            or (
                                                i_comp > 100
                                                and inner_comp > 100
                                                and (i, j, row_index, column_index)
                                                not in intermediate_pairs
                                            )
                                        ):
                                            continue

                                        for reaction in simulation.reactions:
                                            comp_pair = [i_comp, inner_comp]
                                            reactants = [
                                                get_component_index(comp)
                                                for comp in reaction.reactants
                                            ]
                                            products = [
                                                get_component_index(comp)
                                                for comp in reaction.products
                                            ]
                                            intermediates = []
                                            if reaction.hasIntermediate:
                                                intermediates.append(
                                                    (reactants[0] + reactants[1]) * 100
                                                    + reactants[0] * 10
                                                )
                                                intermediates.append(
                                                    (reactants[0] + reactants[1]) * 100
                                                    + reactants[1] * 10
                                                )

                                            if comp_pair == reactants:
                                                poss_reac_index += 1
                                                possible_reactions.append(
                                                    {
                                                        "index": poss_reac_index,
                                                        "products": (
                                                            intermediates
                                                            if reaction.hasIntermediate
                                                            else products
                                                        ),
                                                        "products_position": (
                                                            current_position,
                                                            (row_index, column_index),
                                                        ),
                                                        "reaction_probability": reaction.Pr[
                                                            0
                                                        ],
                                                    }
                                                )
                                            elif comp_pair == reactants[::-1]:
                                                poss_reac_index += 1
                                                possible_reactions.append(
                                                    {
                                                        "index": poss_reac_index,
                                                        "products": (
                                                            intermediates
                                                            if reaction.hasIntermediate
                                                            else products
                                                        ),
                                                        "products_position": (
                                                            (row_index, column_index),
                                                            current_position,
                                                        ),
                                                        "reaction_probability": reaction.Pr[
                                                            0
                                                        ],
                                                    }
                                                )
                                            elif comp_pair == products:
                                                poss_reac_index += 1
                                                possible_reactions.append(
                                                    {
                                                        "index": poss_reac_index,
                                                        "products": (
                                                            intermediates
                                                            if reaction.hasIntermediate
                                                            else reactants
                                                        ),
                                                        "products_position": (
                                                            current_position,
                                                            (row_index, column_index),
                                                        ),
                                                        "reaction_probability": reaction.reversePr[
                                                            (
                                                                0
                                                                if not reaction.hasIntermediate
                                                                else 1
                                                            )
                                                        ],
                                                    }
                                                )
                                            elif comp_pair == products[::-1]:
                                                poss_reac_index += 1
                                                possible_reactions.append(
                                                    {
                                                        "index": poss_reac_index,
                                                        "products": (
                                                            intermediates
                                                            if reaction.hasIntermediate
                                                            else reactants
                                                        ),
                                                        "products_position": (
                                                            (row_index, column_index),
                                                            current_position,
                                                        ),
                                                        "reaction_probability": reaction.reversePr[
                                                            (
                                                                0
                                                                if not reaction.hasIntermediate
                                                                else 1
                                                            )
                                                        ],
                                                    }
                                                )
                                            elif comp_pair == intermediates:
                                                poss_reac_index += 1
                                                possible_reactions.append(
                                                    {
                                                        "index": poss_reac_index,
                                                        "products": products,
                                                        "products_position": (
                                                            current_position,
                                                            (row_index, column_index),
                                                        ),
                                                        "reaction_probability": reaction.Pr[
                                                            1
                                                        ],
                                                    }
                                                )
                                                poss_reac_index += 1
                                                possible_reactions.append(
                                                    {
                                                        "index": poss_reac_index,
                                                        "products": reactants,
                                                        "products_position": (
                                                            current_position,
                                                            (row_index, column_index),
                                                        ),
                                                        "reaction_probability": reaction.reversePr[
                                                            0
                                                        ],
                                                    }
                                                )
                                            elif comp_pair == intermediates[::-1]:
                                                poss_reac_index += 1
                                                possible_reactions.append(
                                                    {
                                                        "index": poss_reac_index,
                                                        "products": products,
                                                        "products_position": (
                                                            (row_index, column_index),
                                                            current_position,
                                                        ),
                                                        "reaction_probability": reaction.Pr[
                                                            1
                                                        ],
                                                    }
                                                )
                                                poss_reac_index += 1
                                                possible_reactions.append(
                                                    {
                                                        "index": poss_reac_index,
                                                        "products": reactants,
                                                        "products_position": (
                                                            (row_index, column_index),
                                                            current_position,
                                                        ),
                                                        "reaction_probability": reaction.reversePr[
                                                            0
                                                        ],
                                                    }
                                                )

                                if len(possible_reactions) > 0:
                                    # Choose which reaction to execute based on their probabilities
                                    individual_probs = [
                                        (
                                            poss_reaction["reaction_probability"],
                                            1 - poss_reaction["reaction_probability"],
                                        )
                                        for poss_reaction in possible_reactions
                                    ]
                                    true_sum = sum(prob[0] for prob in individual_probs)

                                    if true_sum == 0:
                                        # No reaction occurs, so we can skip this step
                                        for poss_reaction in possible_reactions:
                                            not_reacted_components.add(
                                                poss_reaction["products_position"][0]
                                            )
                                            not_reacted_components.add(
                                                poss_reaction["products_position"][1]
                                            )
                                        continue

                                    false_sum = sum(
                                        prob[1] for prob in individual_probs
                                    )
                                    total_sum = true_sum + false_sum

                                    # Add the no-reaction option to the list of probabilities
                                    possible_reactions.append(
                                        {
                                            "index": -1,
                                            "products": None,
                                            "products_position": None,
                                            "reaction_probability": false_sum,
                                        }
                                    )
                                    # Normalize the probabilities
                                    normalized_probabilities = [
                                        poss_reaction["reaction_probability"]
                                        / total_sum
                                        for poss_reaction in possible_reactions
                                    ]

                                    # Choose a reaction based on the normalized probabilities
                                    chosen_reaction = random_generator.choice(
                                        possible_reactions, p=normalized_probabilities
                                    )

                                    chosen_products = chosen_reaction[
                                        "products_position"
                                    ]
                                    if chosen_products is not None:
                                        prod1_pos, prod2_pos = chosen_products

                                        prod1_row, prod1_column = prod1_pos
                                        prod2_row, prod2_column = prod2_pos

                                        if (
                                            M[prod1_row, prod1_column] > 100
                                            and M[prod2_row, prod2_column] > 100
                                        ):
                                            # If the reactants are intermediates, remove their positions from the intermediate pairs (at this moment, there are reactants yet)
                                            intermediate_pairs.remove(
                                                (
                                                    prod1_row,
                                                    prod1_column,
                                                    prod2_row,
                                                    prod2_column,
                                                )
                                            )
                                            intermediate_pairs.remove(
                                                (
                                                    prod2_row,
                                                    prod2_column,
                                                    prod1_row,
                                                    prod1_column,
                                                )
                                            )

                                        prod_1 = chosen_reaction["products"][0]
                                        prod_2 = chosen_reaction["products"][1]

                                        # Reaction
                                        M[prod1_row, prod1_column] = prod_1
                                        M[prod2_row, prod2_column] = prod_2

                                        reacted_components.add(
                                            (prod1_row, prod1_column)
                                        )
                                        reacted_components.add(
                                            (prod2_row, prod2_column)
                                        )

                                        # Add not reacted components to the set for each possible reactions that was not chosen
                                        not_reacted_components.update(
                                            (
                                                poss_reaction["products_position"][0],
                                                poss_reaction["products_position"][1],
                                            )
                                            for poss_reaction in possible_reactions
                                            if poss_reaction["index"]
                                            != chosen_reaction["index"]
                                            and poss_reaction["index"] != -1
                                        )

                                        # If the products are intermediates, store their positions to avoid reacting to other intermediates
                                        if prod_1 > 100 and prod_2 > 100:
                                            intermediate_pairs.append(
                                                (
                                                    prod1_row,
                                                    prod1_column,
                                                    prod2_row,
                                                    prod2_column,
                                                )
                                            )
                                            intermediate_pairs.append(
                                                (
                                                    prod2_row,
                                                    prod2_column,
                                                    prod1_row,
                                                    prod1_column,
                                                )
                                            )
                                    else:
                                        not_reacted_components.update(
                                            (
                                                poss_reaction["products_position"][0],
                                                poss_reaction["products_position"][1],
                                            )
                                            for poss_reaction in possible_reactions
                                            if poss_reaction["index"] != -1
                                        )
                            except Exception as e:
                                iteration_log_text.write(f"  Iteration: {n}\n")
                                iteration_log_text.write(
                                    f"  Current Position: {current_position}\n"
                                )
                                iteration_log_text.write(f"  Component: {i_comp}\n")
                                iteration_log_text.write(
                                    f"  Inner Neighbors: {inner_neighbors_position}\n"
                                )
                                iteration_log_text.write(
                                    f"  Outer Neighbors: {outer_neighbors_position}\n"
                                )
                                iteration_log_text.write(
                                    f"  Current matrix:\n{M}\n"
                                )
                                iteration_log_text.write(
                                    f"  Moved Components: {moved_components}\n"
                                )
                                iteration_log_text.write(
                                    f"  Reacted Components: {reacted_components}\n"
                                )
                                iteration_log_text.write(
                                    f"  Possible Reactions: {possible_reactions}\n"
                                )
                                iteration_log_text.write(f"  True Sum: {true_sum}\n")
                                iteration_log_text.write(f"  False Sum: {false_sum}\n")
                                iteration_log_text.write(f"  Total Sum: {total_sum}\n")
                                iteration_log_text.write(
                                    f"  Normalized Probabilities: {normalized_probabilities}\n"
                                )
                                iteration_log_text.write(
                                    f"  Chosen Reaction: {chosen_reaction}\n"
                                )
                                logger.exception(iteration_log_text.getvalue())
                                raise e
                        if (
                            current_position in moved_components
                            or current_position in reacted_components
                            # i_comp >= 100 means that it is an intermediate component and it cannot move
                            or i_comp > 100
                        ):
                            continue
                        try:
                            occupied_inner_neighbors = []

                            J_neighbors = []
                            j_components = 0

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
                                        if outer_component > 100:
                                            # If the outer component is an intermediate, the joining probability is 0
                                            J_neighbors.append((i_p, 0))
                                            continue
                                        if outer_component != 0:
                                            # Search in the list for the probability J of the component
                                            j_components = next(
                                                (
                                                    j_param.value
                                                    for j_param in parameters.J
                                                    if (
                                                        get_component_index(
                                                            j_param.relation[0]
                                                        )
                                                        == i_comp
                                                        and get_component_index(
                                                            j_param.relation[1]
                                                        )
                                                        == outer_component
                                                    )
                                                    or (
                                                        get_component_index(
                                                            j_param.relation[0]
                                                        )
                                                        == outer_component
                                                        and get_component_index(
                                                            j_param.relation[1]
                                                        )
                                                        == i_comp
                                                    )
                                                )
                                            )
                                        J_neighbors.append((i_p, j_components))
                                    else:
                                        occupied_inner_neighbors.append(
                                            (row_index, column_index)
                                        )

                            # If there is no empty neighbor, the component cannot move
                            if len(J_neighbors) == 0:
                                continue

                            J_max = max(J_neighbors, key=lambda x: x[1])

                            if J_max[1] < 1 and J_max[1] > 0:
                                # Check if there are empty neighbors with J = 0, if so, pick one randomly
                                J_0 = list(filter(lambda x: x[1] == 0, J_neighbors))
                                if len(J_0) > 0:
                                    # Pick one randomly one of the empty neighbors with J = 0
                                    J_max = random_generator.choice(J_0)
                                else:
                                    continue
                            elif J_max[1] == 0:
                                # If J_max is 0, all empty neighbors have J = 0 and are equal in terms of "afinity", so pick one randomly
                                J_max = random_generator.choice(J_neighbors)
                            elif J_max[1] > 0:
                                # If J_max is not 0, pick the empty neighbor with the highest J value
                                J_neigh_max = list(
                                    filter(lambda x: x[1] == J_max[1], J_neighbors)
                                )
                                if len(J_neigh_max) > 1:
                                    # If there are more than one neighbor with the same J_max value, pick one randomly
                                    J_max = random_generator.choice(J_neigh_max)

                            pbs_product = 1

                            if len(occupied_inner_neighbors) > 0:
                                pb_inner_components = []
                                for comp_position in occupied_inner_neighbors:
                                    row, column = comp_position
                                    comp_index = M[row, column]
                                    pair_list = [comp_index, i_comp]
                                    pair_list.sort()
                                    pair = tuple(pair_list)
                                    pb = 1 if comp_index > 100 else pbs[pair]
                                    pb_inner_components.append(pb)

                                pbs_product = np.array(pb_inner_components).prod()

                            pm_total_component = parameters.Pm[i_comp - 1] * pbs_product

                            if Calculations.maybe_execute(pm_total_component):
                                # Move the component to the empty neighbor with the highest J value
                                row_move, column_move = inner_neighbors_position[
                                    int(J_max[0])
                                ]
                                M[row_move, column_move] = i_comp
                                M[i, j] = 0
                                moved_components.add((row_move, column_move))
                                break
                        except Exception as e:
                            iteration_log_text.write(f"  Iteration: {n}\n")
                            iteration_log_text.write(
                                f"  Current Position: {current_position}\n"
                            )
                            iteration_log_text.write(f"  Component: {i_comp}\n")
                            iteration_log_text.write(
                                f"  Inner Neighbors: {inner_neighbors_position}\n"
                            )
                            iteration_log_text.write(
                                f"  Outer Neighbors: {outer_neighbors_position}\n"
                            )
                            iteration_log_text.write(f"  Current matrix:\n{M}\n")
                            iteration_log_text.write(
                                f"  Moved Components: {moved_components}\n"
                            )
                            iteration_log_text.write(
                                f"  Reacted Components: {reacted_components}\n"
                            )
                            iteration_log_text.write(f"  J_neighbors: {J_neighbors}\n")
                            iteration_log_text.write(
                                f"  Occupied Inner Neighbors: {occupied_inner_neighbors}\n"
                            )
                            iteration_log_text.write(f"  J_max: {J_max}\n")
                            iteration_log_text.write(f"  J_0: {J_0}\n")
                            iteration_log_text.write(f"  J_neigh_max: {J_neigh_max}\n")
                            iteration_log_text.write(
                                f"  Pbs for inner components: {pb_inner_components}\n"
                            )
                            iteration_log_text.write(
                                f"  pm_total_component: {pm_total_component}\n"
                            )
                            logger.exception(iteration_log_text.getvalue())
                            raise e
            M_iter[n, :, :] = M.copy()

        print("Final matrix:")
        Calculations.show_matrix(M)

        logger.info("Calculations completed successfully!")

        return M_iter

    @staticmethod
    def show_matrix(M: np.ndarray):
        NL, NC = M.shape
        for i in range(NL):
            for j in range(NC):
                print(f"{M[i, j]:4d}", end=" ")
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
            (get_component_index(j.relation[0]), get_component_index(j.relation[1])): (
                3 / 2
            )
            / (j.value + (3 / 2))
            for j in js
        }
