from typing import List, Set, Tuple


class SimulationState:
    """Encapsulates the simulation state during iterations"""

    def __init__(self, nl: int, nc: int, n_comp: int, n_cell: int):
        self.moved_components: Set[Tuple[int, int]] = set()
        self.reacted_components: Set[Tuple[int, int]] = set()
        self.not_reacted_components: Set[Tuple[int, int]] = set()
        self.intermediate_pairs: List[Tuple[int, int, int, int]] = []
        self.nl = nl
        self.nc = nc
        self.n_comp = n_comp
        self.n_cell = n_cell

    def clear_iteration_state(self):
        """Clears the state between iterations"""
        self.moved_components.clear()
        self.reacted_components.clear()
        self.not_reacted_components.clear()
