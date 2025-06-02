from datetime import datetime
from enum import Enum
from io import StringIO
from math import floor

import numpy as np
from logger import logger
from schemas import PairParameter, RotationInfo, SimulationBase
from utils import get_component_index, get_component_letter

SurfaceTypes = Enum("SurfaceType", [("Torus", 1), ("Cylinder", 2), ("Box", 3)])

VON_NEUMANN_NEIGH = np.array([[-1, 0], [0, -1], [1, 0], [0, 1]], dtype=np.int16)

class Calculations:
    def __init__(self, simulation: SimulationBase):
        self.NL = 0
        self.NC = 0
        self.NEMPTY = 0
        self.M_iter = np.ndarray
        self.molar_fractions_table: list
        self.simulation = simulation

    @staticmethod
    def calculate_cell_counts(total: int, percentages: list[float]) -> list[int]:
        """
        Calculate the number of cells for each component based on their molar fractions.
        The function takes the total number of cells and a list of percentages, and returns a list of cell counts for each component.
        The function ensures that the total number of cells is preserved by rounding the fractional counts and adjusting them if necessary.
        Args:
            total (int): The total number of cells.
            percentages (list[float]): A list of percentages representing the molar fractions of each component.
        Returns:
            list[int]: A list of cell counts for each component.
        """
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

    async def calculate_cellular_automata(self):
        print(self.NL, self.NC)
        simulation = self.simulation
        self.NL = self.simulation.gridHeight
        self.NC = self.simulation.gridLenght

        NL = self.NL
        NC = self.NC

        surface_type = SurfaceTypes.Torus

        NTOT = NC * NL

        EMPTY_FRAC = 0.31  # Fraction of empty cells

        self.NEMPTY = floor(EMPTY_FRAC * NTOT)
        NCELL = NTOT - self.NEMPTY

        components = simulation.ingredients
        parameters = simulation.parameters

        rotation_info: RotationInfo = {"component": -1, "p_rot": 0, "states": [0]}

        if (
            simulation.rotation.component != ""
            and simulation.rotation.component != "None"
        ):
            rot_comp_index = get_component_index(simulation.rotation.component) * 10
            rotation_info = {
                "component": get_component_index(simulation.rotation.component),
                "p_rot": simulation.rotation.Prot,
                "states": [rot_comp_index + i for i in range(1, 5)],
            }

        NCOMP = len(components)

        print(NCOMP)

        NOME_COMP = [component.name for component in components]

        print(NOME_COMP)

        Ci = np.array([comp.molarFraction for comp in components])

        print(Ci)
        Ni = Calculations.calculate_cell_counts(NCELL, Ci)

        M = np.zeros((NL, NC), dtype=np.int16)

        random_generator = np.random.default_rng()

        # Randomly distribute the components in the matrix
        for i in range(NCOMP):
            for j in range(Ni[i]):
                while True:
                    r = np.random.randint(0, NL)
                    c = np.random.randint(0, NC)
                    if M[r, c] == 0:
                        comp_index = i + 1
                        if rotation_info["component"] == comp_index:
                            # Assign the component to one of its states randomly
                            comp_index = random_generator.choice(
                                rotation_info["states"]
                            )
                        M[r, c] = comp_index
                        break

        # Show the matrix formatting the output as a table
        # print("Initial matrix:")
        # Calculations.show_matrix(M)

        # Define the Von Neumann neighborhood
        # North, West, South, East
        

        n_iter = simulation.iterationsNumber

        pbs = Calculations.calculate_pbs(parameters.J)

        moved_components = set()
        reacted_components = set()
        not_reacted_components = set()

        logger.info(
            "Simulation Inputs:\n"
            f"  Grid Dimensions: Lines={NL}, Columns={NC}\n"
            f"  Number of Components: NCOMP={NCOMP}\n"
            f"  Component Names: {NOME_COMP}\n"
            f"  Molar Fractions (Ci): {Ci}\n"
            f"  Cell Counts (Ni): {Ni}\n"
            f"  Surface Type: {surface_type}\n"
            f"  Empty Cells: NEMPTY={self.NEMPTY}\n"
            f"  Occupied Cells: NCELL={NCELL}\n"
            f"  Number of Iterations: n_iter={n_iter}"
        )

        iteration_log_text = StringIO()

        intermediate_pairs = []

        # Create the empty array to store the matrix at each iteration
        self.M_iter = np.zeros((n_iter + 1, NL, NC), dtype=np.int16)

        # Store the initial matrix in the first slice of Calculations.M_iter
        self.M_iter[0, :, :] = M.copy()

        # Prepare the table of molar fractions
        rot_comp_index = rotation_info["component"]

        molar_fractions_header = (
            ["Iteration"]
            + [comp.name for comp in simulation.ingredients]
            + ["Intermediate"]
        )

        molar_fractions_data = np.zeros(
            (n_iter + 1, len(simulation.ingredients) + 2), dtype=np.float16
        ).tolist()
        molar_fractions_data[0] = self.get_molar_fractions(
            M, 0, NCOMP, NCELL, rot_comp_index
        )

        # Start the cronometer
        start_time = datetime.now()

        print("Running simulation")

        for n in range(1, n_iter + 1):
            moved_components.clear()
            reacted_components.clear()
            not_reacted_components.clear()
            for i in range(NL):
                for j in range(NC):
                    current_position = (i, j)
                    i_comp = M[i, j]
                    inner_neighbors_position = VON_NEUMANN_NEIGH + current_position
                    outer_neighbors_position = 2 * VON_NEUMANN_NEIGH + current_position

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

                    if Calculations.is_component(i_comp):
                        # Component rotation
                        if Calculations.is_rotation_component(i_comp):
                            # Check the inner neighbors. If there is at least one occupied neighbor, the component cannot rotate
                            can_rotate = True
                            for inner_neighbor_pos in inner_neighbors_position:
                                row_index, column_index = inner_neighbor_pos
                                coordinates = self.check_constraints(
                                    surface_type, row_index, column_index
                                )
                                if coordinates is not None:
                                    inner_pos_tuple = coordinates
                                    row_index, column_index = inner_pos_tuple
                                    inner_comp = M[row_index, column_index]
                                    if Calculations.is_component(inner_comp):
                                        # The component cannot rotate
                                        can_rotate = False
                                        break
                            if can_rotate and Calculations.should_execute(
                                simulation.rotation.Prot
                            ):
                                # Rotate the component
                                states = rotation_info["states"]
                                M[i, j] = random_generator.choice(
                                    list(filter(lambda x: x != int(i_comp), states))
                                )
                                continue
                        if (
                            current_position not in reacted_components
                            and not Calculations.is_rotation_component(i_comp)
                        ):
                            try:
                                # Scan all the neighbors of the component to get all reaction pairs
                                possible_reactions = []
                                poss_reac_index = 0
                                for inner_neighbor_pos in inner_neighbors_position:
                                    row_index, column_index = inner_neighbor_pos
                                    coordinates = self.check_constraints(
                                        surface_type, row_index, column_index
                                    )
                                    if coordinates is not None:
                                        inner_pos_tuple = coordinates
                                        row_index, column_index = inner_pos_tuple
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
                                            Calculations.is_empty(inner_comp)
                                            or inner_comp == i_comp
                                            or positions_pair in not_reacted_components
                                            or reversed_positions_pair
                                            in not_reacted_components
                                            or inner_pos_tuple in reacted_components
                                            # TODO: maybe this condition is not needed
                                            or inner_pos_tuple in moved_components
                                            # Exclude the case where both components are intermediates but are not a pair (avoid single intermediates in the grid)
                                            or (
                                                Calculations.is_intermediate_component(
                                                    i_comp
                                                )
                                                and Calculations.is_intermediate_component(
                                                    inner_comp
                                                )
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

                                    false_sum = 0

                                    # Add the no-reaction option to the list of probabilities if it is not an intermediate
                                    if not Calculations.is_intermediate_component(
                                        i_comp
                                    ):
                                        false_sum = sum(
                                            prob[1] for prob in individual_probs
                                        )
                                        possible_reactions.append(
                                            {
                                                "index": -1,
                                                "products": None,
                                                "products_position": None,
                                                "reaction_probability": false_sum,
                                            }
                                        )

                                    total_sum = true_sum + false_sum

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

                                        if Calculations.is_intermediate_component(
                                            M[prod1_row, prod1_column]
                                        ) and Calculations.is_intermediate_component(
                                            M[prod2_row, prod2_column]
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
                                        if Calculations.is_intermediate_component(
                                            prod_1
                                        ) and Calculations.is_intermediate_component(
                                            prod_2
                                        ):
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
                                iteration_log_text.write(f"  Current matrix:\n{M}\n")
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
                            or Calculations.is_intermediate_component(i_comp)
                        ):
                            continue
                        try:
                            occupied_inner_neighbors = []

                            J_neighbors = []
                            j_components = 0

                            for i_p in range(len(inner_neighbors_position)):
                                row_index, column_index = inner_neighbors_position[i_p]
                                coordinates = self.check_constraints(
                                    surface_type, row_index, column_index
                                )
                                if coordinates is not None:
                                    row_index, column_index = coordinates
                                    if Calculations.is_empty(
                                        M[row_index, column_index]
                                    ):
                                        o_row, o_column = outer_neighbors_position[i_p]
                                        coordinates = self.check_constraints(
                                            surface_type, o_row, o_column
                                        )
                                        if coordinates is None:
                                            J_neighbors.append((i_p, 0))
                                            continue
                                        outer_component = M[
                                            coordinates[0], coordinates[1]
                                        ]
                                        if Calculations.is_intermediate_component(
                                            outer_component
                                        ):
                                            # If the outer component is an intermediate, the joining probability is 0
                                            J_neighbors.append((i_p, 0))
                                            continue
                                        if Calculations.is_component(outer_component):
                                            # Analyze the direction of rotation components to find the correct J of the interaction
                                            comp1 = ""
                                            comp2 = ""
                                            if Calculations.is_rotation_component(
                                                i_comp
                                            ):
                                                state_side = rotation_info[
                                                    "states"
                                                ].index(i_comp)
                                                # It means that the current component is oriented in the same direction as the outer component
                                                if state_side == i_p:
                                                    comp1 = (
                                                        simulation.rotation.component
                                                        + "1"
                                                    )
                                                    if Calculations.is_rotation_component(
                                                        outer_component
                                                    ):
                                                        outer_state_side = (
                                                            rotation_info[
                                                                "states"
                                                            ].index(outer_component)
                                                        )
                                                        # Check if the outer component is oriented in the opposite direction
                                                        if abs(
                                                            outer_state_side - i_p == 2
                                                        ):
                                                            comp2 = (
                                                                simulation.rotation.component
                                                                + "1"
                                                            )
                                                        else:
                                                            comp2 = (
                                                                simulation.rotation.component
                                                                + "2"
                                                            )
                                                    else:
                                                        comp2 = get_component_letter(
                                                            outer_component
                                                        )
                                                else:
                                                    comp1 = (
                                                        simulation.rotation.component
                                                        + "2"
                                                    )
                                                    if Calculations.is_rotation_component(
                                                        outer_component
                                                    ):
                                                        outer_state_side = (
                                                            rotation_info[
                                                                "states"
                                                            ].index(outer_component)
                                                        )
                                                        # Check if the outer component is oriented in the opposite direction
                                                        if abs(
                                                            outer_state_side - i_p == 2
                                                        ):
                                                            comp2 = (
                                                                simulation.rotation.component
                                                                + "1"
                                                            )
                                                        else:
                                                            comp2 = (
                                                                simulation.rotation.component
                                                                + "2"
                                                            )
                                                    else:
                                                        comp2 = get_component_letter(
                                                            outer_component
                                                        )
                                            else:
                                                comp1 = get_component_letter(i_comp)
                                                if Calculations.is_rotation_component(
                                                    outer_component
                                                ):
                                                    outer_state_side = rotation_info[
                                                        "states"
                                                    ].index(outer_component)
                                                    # Check if the outer component is oriented in the opposite direction
                                                    if abs(outer_state_side - i_p == 2):
                                                        comp2 = (
                                                            simulation.rotation.component
                                                            + "1"
                                                        )
                                                    else:
                                                        comp2 = (
                                                            simulation.rotation.component
                                                            + "2"
                                                        )
                                                else:
                                                    comp2 = get_component_letter(
                                                        outer_component
                                                    )

                                            pair_relation = f"{comp1}|{comp2}"
                                            reversed_pair_relation = f"{comp2}|{comp1}"

                                            # Search in the list for the probability J of the component
                                            j_components = next(
                                                (
                                                    j_param.value
                                                    for j_param in parameters.J
                                                    if (
                                                        j_param.relation
                                                        == pair_relation
                                                        or j_param.relation
                                                        == reversed_pair_relation
                                                    )
                                                )
                                            )
                                        J_neighbors.append((i_p, j_components))
                                    else:
                                        occupied_inner_neighbors.append(
                                            (i_p, row_index, column_index)
                                        )

                            # If there is no empty neighbor, the component cannot move
                            if len(J_neighbors) == 0:
                                continue

                            J_max = max(J_neighbors, key=lambda x: x[1])

                            if J_max[1] < 1 and J_max[1] >= 0:
                                # Check if there are empty neighbors with J = 0, if so, pick one randomly
                                J_0 = list(filter(lambda x: x[1] == 0, J_neighbors))
                                if len(J_0) > 0:
                                    # Pick one randomly one of the empty neighbors with J = 0
                                    J_max = random_generator.choice(J_0)
                                else:
                                    # All components repulse each other, so the component cannot move
                                    continue
                            elif J_max[1] == 0:
                                # If J_max is 0, all empty neighbors have J = 0 and are equal in terms of "afinity", so pick one randomly
                                J_max = random_generator.choice(J_neighbors)
                            elif J_max[1] >= 1:
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
                                for ind_occ, row, column in occupied_inner_neighbors:
                                    comp_index = M[row, column]
                                    comp1 = ""
                                    comp2 = ""
                                    if Calculations.is_rotation_component(i_comp):
                                        # If the component is a rotation component, get the state of the component
                                        state_side = rotation_info["states"].index(
                                            i_comp
                                        )
                                        # Check if the component is oriented in the same direction as the inner component
                                        if state_side == ind_occ:
                                            comp1 = simulation.rotation.component + "1"
                                            if Calculations.is_rotation_component(
                                                comp_index
                                            ):
                                                inner_state_side = rotation_info[
                                                    "states"
                                                ].index(comp_index)
                                                # Check if the inner component is oriented in the opposite direction
                                                if abs(inner_state_side - ind_occ == 2):
                                                    comp2 = (
                                                        simulation.rotation.component
                                                        + "1"
                                                    )
                                                else:
                                                    comp2 = (
                                                        simulation.rotation.component
                                                        + "2"
                                                    )
                                            else:
                                                comp2 = get_component_letter(comp_index)
                                        else:
                                            comp1 = simulation.rotation.component + "2"
                                            if Calculations.is_rotation_component(
                                                comp_index
                                            ):
                                                inner_state_side = rotation_info[
                                                    "states"
                                                ].index(comp_index)
                                                # Check if the inner component is oriented in the opposite direction
                                                if abs(inner_state_side - ind_occ == 2):
                                                    comp2 = (
                                                        simulation.rotation.component
                                                        + "1"
                                                    )
                                                else:
                                                    comp2 = (
                                                        simulation.rotation.component
                                                        + "2"
                                                    )
                                            else:
                                                comp2 = get_component_letter(comp_index)
                                    else:
                                        comp1 = get_component_letter(i_comp)
                                        if Calculations.is_rotation_component(
                                            comp_index
                                        ):
                                            inner_state_side = rotation_info[
                                                "states"
                                            ].index(comp_index)
                                            # Check if the inner component is oriented in the opposite direction
                                            if abs(inner_state_side - ind_occ == 2):
                                                comp2 = (
                                                    simulation.rotation.component + "1"
                                                )
                                            else:
                                                comp2 = (
                                                    simulation.rotation.component + "2"
                                                )
                                        else:
                                            comp2 = get_component_letter(comp_index)

                                    pair_relation = f"{comp1}|{comp2}"
                                    reversed_pair_relation = f"{comp2}|{comp1}"

                                    pb = (
                                        1
                                        if Calculations.is_intermediate_component(
                                            comp_index
                                        )
                                        else (
                                            pbs[pair_relation]
                                            if pair_relation in pbs
                                            else pbs[reversed_pair_relation]
                                        )
                                    )
                                    pb_inner_components.append(pb)

                                pbs_product = np.array(pb_inner_components).prod()

                            pm_total_component = (
                                parameters.Pm[
                                    (
                                        rotation_info["component"]
                                        if Calculations.is_rotation_component(i_comp)
                                        else i_comp
                                    )
                                    - 1
                                ]
                                * pbs_product
                            )

                            if Calculations.should_execute(pm_total_component):
                                # Move the component to the empty neighbor with the highest J value
                                row_move, column_move = inner_neighbors_position[
                                    int(J_max[0])
                                ]
                                row_move, column_move = self.check_constraints(
                                    surface_type, row_move, column_move
                                )
                                M[row_move, column_move] = i_comp
                                M[i, j] = 0
                                moved_components.add((row_move, column_move))

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
            self.M_iter[n, :, :] = M.copy()
            molar_fractions_data[n] = Calculations.get_molar_fractions(
                M, n, NCOMP, NCELL, rot_comp_index
            )
            if n % 10 == 0 or n == n_iter:
                yield n, n_iter

        self.molar_fractions_table = [
            molar_fractions_header,
            *molar_fractions_data,
        ]

        # Calculations.show_matrix(M)

        logger.info("Calculations completed successfully!")

        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        print(f"Elapsed time: {elapsed_time:.2f} seconds")

    @staticmethod
    def is_intermediate_component(i_comp):
        return i_comp > 200

    @staticmethod
    def is_empty(inner_comp):
        return inner_comp == 0

    @staticmethod
    def is_rotation_component(i_comp):
        return i_comp > 10 and i_comp < 200

    @staticmethod
    def is_component(i_comp):
        return i_comp > 0

    @staticmethod
    def show_matrix(M: np.ndarray):
        NL, NC = M.shape
        for i in range(NL):
            for j in range(NC):
                print(f"{M[i, j]:4d}", end=" ")
            print()
        print()

    @staticmethod
    def should_execute(probability: float) -> bool:
        """
        Determine whether to execute an action based on a given probability.
        Args:
            probability (float): The probability of executing the action.
        Returns:
            bool: True if the action should be executed, False otherwise.
        """
        return np.random.random() < probability

    def check_constraints(
        self, surface_type: SurfaceTypes, r: int, c: int
    ) -> tuple[int, int] | None:
        """
        Check the constraints for the given surface type and coordinates.
        Args:
            surface_type (SurfaceTypes): The type of surface (Box, Cylinder, Torus).
            r (int): Row index.
            c (int): Column index.
        Returns:
            tuple[int, int] | None: Validated coordinates or None if out of bounds.
        """
        if surface_type == SurfaceTypes.Box:
            return (
                (r, c)
                if r >= 0 and r < self.NL and c >= 0 and c < self.NC
                else None
            )
        if surface_type == SurfaceTypes.Cylinder:
            return (r, c % self.NC) if r >= 0 and r < self.NL else None
        if surface_type == SurfaceTypes.Torus:
            return (r % self.NL, c % self.NC)

    @staticmethod
    def calculate_pbs(js: list[PairParameter]):
        """
        Calculate the breaking probabilities (Pb) of each pair of components based on the J values.
        Args:
            js (list[PairParameter]): List of PairParameter objects containing J values.
        Returns:
            dict: Dictionary with component pairs as keys and their corresponding Pb values.
        """
        return {j.relation: (3 / 2) / (j.value + (3 / 2)) for j in js}

    @staticmethod
    def get_molar_fractions(
        M: np.ndarray,
        current_iteration: int,
        n_comp: int,
        n_cell: int,
        rot_comp_index=-1,
    ) -> list[float]:
        """
        Calculate the molar fractions of each component in the matrix M.
        Args:
            M (np.ndarray): The matrix representing the system.
            current_iteration (int): The current iteration number.
            n_comp (int): The number of components.
            n_cell (int): The total number of cells in the matrix.
            rot_comp_index (int, optional): Index for rotation components. Defaults to -1.
        Returns:
            list[float]: List of molar fractions for each component.
        """
        count_line = np.zeros(n_comp + 2, dtype=np.int16)

        nl, nc = M.shape

        # Count the number of each component in the matrix
        for i in range(nl):
            for j in range(nc):
                comp = M[i, j]
                if not Calculations.is_empty(comp):
                    if Calculations.is_intermediate_component(comp):
                        count_line[-1] += 1
                    elif Calculations.is_rotation_component(comp):
                        count_line[rot_comp_index] += 1
                    else:
                        count_line[comp] += 1

        molar_fractions_line = count_line / n_cell
        molar_fractions_line[0] = current_iteration
        molar_fractions_line = molar_fractions_line.tolist()
        return molar_fractions_line

    def get_results(self) -> tuple[np.ndarray, list[list]]:
        return self.M_iter, self.molar_fractions_table
