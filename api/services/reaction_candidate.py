from typing import List, Tuple


class ReactionCandidate:
    """Representa uma reação candidata"""

    def __init__(
        self,
        index: int,
        products: List[int],
        products_position: Tuple[Tuple[int, int], Tuple[int, int]],
        reaction_probability: float,
    ):
        self.index = index
        self.products = products
        self.products_position = products_position
        self.reaction_probability = reaction_probability
