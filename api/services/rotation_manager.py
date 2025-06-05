from typing import Tuple
import numpy as np
from schemas import RotationInfo
from services.calculations_helper import VON_NEUMANN_NEIGH, SurfaceTypes, is_component


class RotationManager:
    """Gerencia rotação de componentes"""

    def __init__(self, rotation_info: RotationInfo):
        self.rotation_info = rotation_info

    def can_rotate(
        self,
        matrix: np.ndarray,
        position: Tuple[int, int],
        surface_type: SurfaceTypes,
        constraint_checker,
    ) -> bool:
        """Verifica se um componente pode rotacionar"""
        inner_neighbors_position = VON_NEUMANN_NEIGH + np.array(position)

        for neighbor_pos in inner_neighbors_position:
            row_idx, col_idx = neighbor_pos
            coordinates = constraint_checker(surface_type, row_idx, col_idx)

            if coordinates is not None:
                row_idx, col_idx = coordinates
                if is_component(matrix[row_idx, col_idx]):
                    return False

        return True

    def rotate_component(
        self, matrix: np.ndarray, position: Tuple[int, int], current_component: int
    ):
        """Rotaciona um componente para um novo estado"""
        states = self.rotation_info["states"]
        available_states = [state for state in states if state != current_component]

        if available_states:
            new_state = np.random.choice(available_states)
            matrix[position[0], position[1]] = new_state
