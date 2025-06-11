from typing import List, Set, Tuple


class SimulationState:
    """Encapsulates the simulation state during iterations"""

    def __init__(self):
        self.moved_components: Set[Tuple[int, int]] = set()
        self.reacted_components: Set[Tuple[int, int]] = set()
        self.not_reacted_components: Set[Tuple[int, int]] = set()
        self.intermediate_pairs: List[Tuple[int, int, int, int]] = []

    def clear_iteration_state(self):
        """Clears the state between iterations"""
        self.moved_components.clear()
        self.reacted_components.clear()
        self.not_reacted_components.clear()
