from enum import Enum
from typing import Dict, List
import numpy as np

from domain.schemas import PairParameter

# North, West, South, East
VON_NEUMANN_NEIGH = np.array([[-1, 0], [0, -1], [1, 0], [0, 1]], dtype=np.int16)

SurfaceTypes = Enum("SurfaceType", [("Torus", 1), ("Cylinder", 2), ("Box", 3)])

def is_intermediate_component(i_comp: int) -> bool:
    return i_comp > 200

def is_empty(inner_comp: int) -> bool:
    return inner_comp == 0

def is_rotation_component(i_comp: int) -> bool:
    return 10 < i_comp < 200

def is_component(i_comp: int) -> bool:
    return i_comp > 0

def should_execute(probability: float) -> bool:
    return np.random.random() < probability

def calculate_pbs(js: List[PairParameter]) -> Dict[str, float]:
    return {j.relation: (3 / 2) / (j.value + (3 / 2)) for j in js}

def get_molar_fractions(
    M: np.ndarray,
    current_iteration: int,
    n_comp: int,
    n_cell: int,
    rot_comp_index: int = -1,
) -> List[float]:
    count_line = np.zeros(n_comp + 2, dtype=np.int16)

    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            comp = M[i, j]
            if not is_empty(comp):
                if is_intermediate_component(comp):
                    count_line[-1] += 1
                elif is_rotation_component(comp):
                    count_line[rot_comp_index] += 1
                else:
                    count_line[comp] += 1

    molar_fractions_line = count_line / n_cell
    molar_fractions_line[0] = current_iteration
    return molar_fractions_line.tolist()
