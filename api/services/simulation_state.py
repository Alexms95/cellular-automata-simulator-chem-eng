from typing import List, Set, Tuple


class SimulationState:
    """Encapsula o estado da simulação durante as iterações"""

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
        """Limpa o estado entre iterações"""
        self.moved_components.clear()
        self.reacted_components.clear()
        self.not_reacted_components.clear()
