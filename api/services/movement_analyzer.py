from typing import Dict, List, Optional, Tuple
import numpy as np

from services.calculations_helper import SurfaceTypes
from schemas import Parameters, RotationInfo, SimulationBase
from services.calculations_helper import VON_NEUMANN_NEIGH, is_component, is_empty, is_intermediate_component, is_rotation_component
from utils import get_component_letter


class MovementAnalyzer:
    """Analisa possibilidades de movimento de componentes"""

    def __init__(
        self,
        simulation: SimulationBase,
        rotation_info: RotationInfo,
        parameters: Parameters,
        pbs: Dict[str, float],
    ):
        self.simulation = simulation
        self.rotation_info = rotation_info
        self.parameters = parameters
        self.pbs = pbs

    def analyze_movement_possibility(
        self,
        matrix: np.ndarray,
        position: Tuple[int, int],
        component: int,
        surface_type: SurfaceTypes,
        constraint_checker,
    ) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """
        Analisa se um componente pode se mover e para onde.

        Returns:
            Tuple[bool, Optional[Tuple[int, int]], float]: (can_move, target_position, probability)
        """
        i, j = position
        inner_neighbors_position = VON_NEUMANN_NEIGH + np.array(position)
        outer_neighbors_position = 2 * VON_NEUMANN_NEIGH + np.array(position)

        j_neighbors = self._calculate_j_neighbors(
            matrix,
            inner_neighbors_position,
            outer_neighbors_position,
            component,
            surface_type,
            constraint_checker,
        )

        if not j_neighbors:
            return False, None, 0.0

        target_neighbor = self._select_target_neighbor(j_neighbors)
        if target_neighbor is None:
            return False, None, 0.0

        occupied_inner_neighbors = self._get_occupied_inner_neighbors(
            matrix, inner_neighbors_position, surface_type, constraint_checker
        )

        movement_probability = self._calculate_movement_probability(
            component, occupied_inner_neighbors, matrix
        )

        target_position = inner_neighbors_position[int(target_neighbor[0])]
        validated_position = constraint_checker(surface_type, *target_position)

        return True, validated_position, movement_probability

    def _calculate_j_neighbors(
        self,
        matrix: np.ndarray,
        inner_neighbors_position: np.ndarray,
        outer_neighbors_position: np.ndarray,
        component: int,
        surface_type: SurfaceTypes,
        constraint_checker,
    ) -> List[Tuple[int, float]]:
        """Calcula os valores J para vizinhos vazios"""
        j_neighbors = []

        for i_p in range(len(inner_neighbors_position)):
            row_idx, col_idx = inner_neighbors_position[i_p]
            coordinates = constraint_checker(surface_type, row_idx, col_idx)

            if coordinates is None:
                continue

            row_idx, col_idx = coordinates

            if is_empty(matrix[row_idx, col_idx]):
                j_value = self._calculate_j_value_for_position(
                    matrix,
                    component,
                    i_p,
                    outer_neighbors_position,
                    surface_type,
                    constraint_checker,
                )
                j_neighbors.append((i_p, j_value))

        return j_neighbors

    def _calculate_j_value_for_position(
        self,
        matrix: np.ndarray,
        component: int,
        position_index: int,
        outer_neighbors_position: np.ndarray,
        surface_type: SurfaceTypes,
        constraint_checker,
    ) -> float:
        """Calcula o valor J para uma posição específica"""
        o_row, o_column = outer_neighbors_position[position_index]
        coordinates = constraint_checker(surface_type, o_row, o_column)

        if coordinates is None:
            return 0.0

        outer_component = matrix[coordinates[0], coordinates[1]]

        if is_intermediate_component(
            outer_component
        ) or not is_component(outer_component):
            return 0.0

        comp1, comp2 = self._get_component_pair_for_interaction(
            component, outer_component, position_index
        )

        return self._find_j_value_for_pair(comp1, comp2)

    def _get_component_pair_for_interaction(
        self, component1: int, component2: int, direction: int
    ) -> Tuple[str, str]:
        """Determina o par de componentes para interação considerando rotação"""
        comp1 = self._get_component_representation(component1, direction)
        comp2 = self._get_component_representation(component2, direction, is_outer=True)
        return comp1, comp2

    def _get_component_representation(
        self, component: int, direction: int, is_outer: bool = False
    ) -> str:
        """Obtém a representação string do componente considerando rotação"""
        if is_rotation_component(component):
            state_side = self.rotation_info["states"].index(component)

            if is_outer:
                # Para componente externo, verificar orientação oposta
                if abs(state_side - direction) == 2:
                    return self.simulation.rotation.component + "1"
                else:
                    return self.simulation.rotation.component + "2"
            else:
                # Para componente interno
                if state_side == direction:
                    return self.simulation.rotation.component + "1"
                else:
                    return self.simulation.rotation.component + "2"
        else:
            return get_component_letter(component)

    def _find_j_value_for_pair(self, comp1: str, comp2: str) -> float:
        """Encontra o valor J para um par de componentes"""
        pair_relation = f"{comp1}|{comp2}"
        reversed_pair_relation = f"{comp2}|{comp1}"

        for j_param in self.parameters.J:
            if j_param.relation in (pair_relation, reversed_pair_relation):
                return j_param.value

        return 0.0

    def _select_target_neighbor(
        self, j_neighbors: List[Tuple[int, float]]
    ) -> Optional[Tuple[int, float]]:
        """Seleciona o vizinho alvo para movimento"""
        if not j_neighbors:
            return None

        j_max = max(j_neighbors, key=lambda x: x[1])

        if j_max[1] < 1 and j_max[1] >= 0:
            j_zero_neighbors = [n for n in j_neighbors if n[1] == 0]
            if j_zero_neighbors:
                return np.random.default_rng().choice(j_zero_neighbors)
            else:
                return None
        elif j_max[1] == 0:
            return np.random.default_rng().choice(j_neighbors)
        else:  # j_max[1] >= 1
            max_j_neighbors = [n for n in j_neighbors if n[1] == j_max[1]]
            return np.random.default_rng().choice(max_j_neighbors)

    def _get_occupied_inner_neighbors(
        self,
        matrix: np.ndarray,
        inner_neighbors_position: np.ndarray,
        surface_type: SurfaceTypes,
        constraint_checker,
    ) -> List[Tuple[int, int, int]]:
        """Obtém vizinhos internos ocupados"""
        occupied = []

        for i_p, (row_idx, col_idx) in enumerate(inner_neighbors_position):
            coordinates = constraint_checker(surface_type, row_idx, col_idx)
            if coordinates is not None:
                row_idx, col_idx = coordinates
                if not is_empty(matrix[row_idx, col_idx]):
                    occupied.append((i_p, row_idx, col_idx))

        return occupied

    def _calculate_movement_probability(
        self,
        component: int,
        occupied_inner_neighbors: List[Tuple[int, int, int]],
        matrix: np.ndarray,
    ) -> float:
        """Calcula a probabilidade de movimento considerando vizinhos ocupados"""
        if not occupied_inner_neighbors:
            component_index = (
                self.rotation_info["component"]
                if is_rotation_component(component)
                else component
            )
            return self.parameters.Pm[component_index - 1]

        pb_values = []
        for ind_occ, row, col in occupied_inner_neighbors:
            neighbor_component = matrix[row, col]

            if is_intermediate_component(neighbor_component):
                pb_values.append(1.0)
            else:
                comp1, comp2 = self._get_component_pair_for_interaction(
                    component, neighbor_component, ind_occ
                )
                pair_relation = f"{comp1}|{comp2}"
                reversed_pair_relation = f"{comp2}|{comp1}"

                pb = self.pbs.get(pair_relation) or self.pbs.get(
                    reversed_pair_relation, 1.0
                )
                pb_values.append(pb)

        pbs_product = np.array(pb_values).prod()
        component_index = (
            self.rotation_info["component"]
            if is_rotation_component(component)
            else component
        )

        return self.parameters.Pm[component_index - 1] * pbs_product
