from typing import List, Tuple

import numpy as np
from schemas import Reaction, RotationInfo, SimulationBase
from services.calculations_helper import (
    VON_NEUMANN_NEIGH,
    SurfaceTypes,
    is_empty,
    is_intermediate_component,
)
from services.reaction_candidate import ReactionCandidate
from services.simulation_state import SimulationState
from utils import get_component_index


class ReactionProcessor:
    """Processes chemical reactions in the simulation"""

    def __init__(self, simulation: SimulationBase, rotation_info: RotationInfo):
        self.simulation = simulation
        self.rotation_info = rotation_info
        self.random_generator = np.random.default_rng()

    def find_possible_reactions(
        self,
        matrix: np.ndarray,
        position: Tuple[int, int],
        component: int,
        surface_type: SurfaceTypes,
        constraint_checker,
        state: SimulationState,
    ) -> List[ReactionCandidate]:
        """Finds all possible reactions for a component"""
        i, j = position
        inner_neighbors_position = VON_NEUMANN_NEIGH + np.array(position)
        possible_reactions = []
        reaction_index = 0

        for neighbor_pos in inner_neighbors_position:
            row_idx, col_idx = neighbor_pos
            coordinates = constraint_checker(surface_type, row_idx, col_idx)

            if coordinates is None:
                continue

            row_idx, col_idx = coordinates
            neighbor_component = matrix[row_idx, col_idx]

            if self._should_skip_neighbor(
                component, neighbor_component, position, coordinates, state
            ):
                continue

            reactions_for_pair = self._find_reactions_for_component_pair(
                component, neighbor_component, position, coordinates, reaction_index
            )
            possible_reactions.extend(reactions_for_pair)
            reaction_index += len(reactions_for_pair)

        return possible_reactions

    def _should_skip_neighbor(
        self,
        component: int,
        neighbor_component: int,
        position: Tuple[int, int],
        neighbor_position: Tuple[int, int],
        state: SimulationState,
    ) -> bool:
        """Determines if a neighbor should be skipped for reactions"""
        positions_pair = (position, neighbor_position)
        reversed_positions_pair = (neighbor_position, position)

        return (
            is_empty(neighbor_component)
            or neighbor_component == component
            or positions_pair in state.not_reacted_components
            or reversed_positions_pair in state.not_reacted_components
            or neighbor_position in state.reacted_components
            or neighbor_position in state.moved_components
            or self._are_unpaired_intermediates(
                component, neighbor_component, position, neighbor_position, state
            )
        )

    def _are_unpaired_intermediates(
        self,
        comp1: int,
        comp2: int,
        pos1: Tuple[int, int],
        pos2: Tuple[int, int],
        state: SimulationState,
    ) -> bool:
        """Checks if two components are unpaired intermediates"""
        if is_intermediate_component(comp1) and is_intermediate_component(comp2):

            i, j, row_idx, col_idx = (*pos1, *pos2)
            return (i, j, row_idx, col_idx) not in state.intermediate_pairs

        return False

    def _find_reactions_for_component_pair(
        self,
        comp1: int,
        comp2: int,
        pos1: Tuple[int, int],
        pos2: Tuple[int, int],
        reaction_index_start: int,
    ) -> List[ReactionCandidate]:
        """Finds reactions for a specific pair of components"""
        reactions = []
        reaction_index = reaction_index_start

        for reaction in self.simulation.reactions:
            reactants = [get_component_index(comp) for comp in reaction.reactants]
            products = [get_component_index(comp) for comp in reaction.products]

            intermediates = []
            if reaction.hasIntermediate:
                intermediates = [
                    (reactants[0] + reactants[1]) * 100 + reactants[0] * 10,
                    (reactants[0] + reactants[1]) * 100 + reactants[1] * 10,
                ]

            comp_pair = [comp1, comp2]

            # Check all possible reaction combinations
            reaction_candidates = self._check_reaction_combinations(
                comp_pair,
                reactants,
                products,
                intermediates,
                reaction,
                pos1,
                pos2,
                reaction_index,
            )

            reactions.extend(reaction_candidates)
            reaction_index += len(reaction_candidates)

        return reactions

    def _check_reaction_combinations(
        self,
        comp_pair: List[int],
        reactants: List[int],
        products: List[int],
        intermediates: List[int],
        reaction: Reaction,
        pos1: Tuple[int, int],
        pos2: Tuple[int, int],
        reaction_index: int,
    ) -> List[ReactionCandidate]:
        """Checks all possible reaction combinations"""
        candidates = []

        # Direct reaction (reactants -> products/intermediates)
        if comp_pair == reactants:
            target_products = intermediates if reaction.hasIntermediate else products
            candidates.append(
                ReactionCandidate(
                    reaction_index, target_products, (pos1, pos2), reaction.Pr[0]
                )
            )
        elif comp_pair == reactants[::-1]:
            target_products = intermediates if reaction.hasIntermediate else products
            candidates.append(
                ReactionCandidate(
                    reaction_index + 1, target_products, (pos2, pos1), reaction.Pr[0]
                )
            )

        # Reverse reaction (products -> reactants/intermediates)
        if comp_pair == products:
            target_products = intermediates if reaction.hasIntermediate else reactants
            prob_index = 1 if reaction.hasIntermediate else 0
            candidates.append(
                ReactionCandidate(
                    reaction_index + 2,
                    target_products,
                    (pos1, pos2),
                    reaction.reversePr[prob_index],
                )
            )
        elif comp_pair == products[::-1]:
            target_products = intermediates if reaction.hasIntermediate else reactants
            prob_index = 1 if reaction.hasIntermediate else 0
            candidates.append(
                ReactionCandidate(
                    reaction_index + 3,
                    target_products,
                    (pos2, pos1),
                    reaction.reversePr[prob_index],
                )
            )

        # Reactions with intermediates
        if intermediates and comp_pair == intermediates:
            # Intermediates -> products
            candidates.append(
                ReactionCandidate(
                    reaction_index + 4, products, (pos1, pos2), reaction.Pr[1]
                )
            )
            # Intermediates -> reactants
            candidates.append(
                ReactionCandidate(
                    reaction_index + 5, reactants, (pos1, pos2), reaction.reversePr[0]
                )
            )
        elif intermediates and comp_pair == intermediates[::-1]:
            candidates.append(
                ReactionCandidate(
                    reaction_index + 6, products, (pos2, pos1), reaction.Pr[1]
                )
            )
            candidates.append(
                ReactionCandidate(
                    reaction_index + 7, reactants, (pos2, pos1), reaction.reversePr[0]
                )
            )

        return candidates

    def select_and_execute_reaction(
        self,
        possible_reactions: List[ReactionCandidate],
        component: int,
        matrix: np.ndarray,
        state: SimulationState,
    ) -> bool:
        """Selects and executes a reaction based on probabilities"""
        if not possible_reactions:
            return False

        # Calculate normalized probabilities
        true_sum = sum(reaction.reaction_probability for reaction in possible_reactions)

        if true_sum == 0:
            self._mark_components_as_not_reacted(possible_reactions, state)
            return False

        # Add no-reaction option for non-intermediates
        if not is_intermediate_component(component):
            false_sum = len(possible_reactions) - true_sum
            no_reaction = ReactionCandidate(-1, [], ((-1, -1), (-1, -1)), false_sum)
            possible_reactions.append(no_reaction)
            total_sum = true_sum + false_sum
        else:
            total_sum = true_sum

        # Normalize probabilities
        normalized_probs = [
            r.reaction_probability / total_sum for r in possible_reactions
        ]

        # Select reaction
        chosen_reaction = self.random_generator.choice(
            possible_reactions, p=normalized_probs
        )

        if chosen_reaction.index == -1:  # No reaction
            self._mark_components_as_not_reacted(possible_reactions[:-1], state)
            return False

        # Execute reaction
        self._execute_reaction(chosen_reaction, matrix, state)
        self._mark_other_reactions_as_not_executed(
            possible_reactions, chosen_reaction, state
        )

        return True

    def _mark_components_as_not_reacted(
        self, reactions: List[ReactionCandidate], state: SimulationState
    ):
        """Marks components as not reacted"""
        for reaction in reactions:
            if reaction.index != -1:
                state.not_reacted_components.add(reaction.products_position[0])
                state.not_reacted_components.add(reaction.products_position[1])

    def _execute_reaction(
        self, reaction: ReactionCandidate, matrix: np.ndarray, state: SimulationState
    ):
        """Executes a specific reaction"""
        pos1, pos2 = reaction.products_position
        prod1, prod2 = reaction.products

        # Remove intermediate pairs if they exist
        if is_intermediate_component(
            matrix[pos1[0], pos1[1]]
        ) and is_intermediate_component(matrix[pos2[0], pos2[1]]):
            self._remove_intermediate_pairs(pos1, pos2, state)

        # Apply products
        matrix[pos1[0], pos1[1]] = prod1
        matrix[pos2[0], pos2[1]] = prod2

        # Mark as reacted
        state.reacted_components.add(pos1)
        state.reacted_components.add(pos2)

        # Add new intermediate pairs if necessary
        if is_intermediate_component(prod1) and is_intermediate_component(prod2):

            self._add_intermediate_pairs(pos1, pos2, state)

    def _remove_intermediate_pairs(
        self, pos1: Tuple[int, int], pos2: Tuple[int, int], state: SimulationState
    ):
        """Removes intermediate pairs from the list"""
        pairs_to_remove = [(*pos1, *pos2), (*pos2, *pos1)]

        for pair in pairs_to_remove:
            if pair in state.intermediate_pairs:
                state.intermediate_pairs.remove(pair)

    def _add_intermediate_pairs(
        self, pos1: Tuple[int, int], pos2: Tuple[int, int], state: SimulationState
    ):
        """Adds new intermediate pairs to the list"""
        state.intermediate_pairs.extend([(*pos1, *pos2), (*pos2, *pos1)])

    def _mark_other_reactions_as_not_executed(
        self,
        all_reactions: List[ReactionCandidate],
        executed_reaction: ReactionCandidate,
        state: SimulationState,
    ):
        """Marks other reactions as not executed"""
        for reaction in all_reactions:
            if reaction.index != executed_reaction.index and reaction.index != -1:
                state.not_reacted_components.add(reaction.products_position[0])
                state.not_reacted_components.add(reaction.products_position[1])
