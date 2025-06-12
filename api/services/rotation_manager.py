from typing import Tuple

import numpy as np
from utils import get_component_index
from domain.schemas import Rotation, RotationInfo
from services.calculations_helper import VON_NEUMANN_NEIGH, SurfaceTypes, is_component


class RotationManager:
    """Manages component rotation"""

    def __init__(self, rotation: Rotation):
        self.__rotation_info = self._setup_rotation_info(rotation)

    def get_rotation_info(self) -> RotationInfo:
        """Returns rotation information"""
        return self.__rotation_info

    def can_rotate(
        self,
        matrix: np.ndarray,
        position: Tuple[int, int],
        surface_type: SurfaceTypes,
        constraint_checker,
    ) -> bool:
        """Checks if a component can rotate"""
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
        """Rotates a component to a new state"""
        states = self.get_rotation_info().get("states", [])

        if not states:
            return
        
        available_states = [state for state in states if state != current_component]

        if available_states:
            new_state = np.random.choice(available_states)
            matrix[position[0], position[1]] = new_state

    def _setup_rotation_info(self, rotation: Rotation) -> RotationInfo:
        """Sets up rotation information"""
        rotation_info: RotationInfo = {"component": -1, "p_rot": 0, "states": [0]}

        if rotation.component and rotation.component != "None":

            rot_comp_index = get_component_index(rotation.component)
            rotation_info = {
                "component": rot_comp_index,
                "p_rot": rotation.Prot,
                "states": [rot_comp_index * 10 + i for i in range(1, 5)],
            }

        return rotation_info
