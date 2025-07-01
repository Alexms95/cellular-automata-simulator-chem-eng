import sys
from pathlib import Path
from typing import Tuple
from unittest.mock import Mock

import numpy as np
import pytest

# Garantir que o diretório da API está no sys.path para importações relativas
sys.path.append(str(Path(__file__).resolve().parent.parent))

from domain.schemas import Reaction
from services.calculations_helper import SurfaceTypes
from services.reaction_candidate import ReactionCandidate
from services.reaction_processor import ReactionProcessor
from services.simulation_state import SimulationState
from utils import get_component_index


class TestReactionProcessor:
    """Testes unitários para a classe ReactionProcessor"""

    # ---------------------------------------------------------------------
    # Fixtures de apoio
    # ---------------------------------------------------------------------

    @pytest.fixture
    def simple_reaction(self) -> Reaction:
        """Reação direta A + B → C + D com probabilidade 1.0"""

        return Reaction(
            reactants=["A", "B"],
            products=["C", "D"],
            Pr=[1.0],  # Probabilidade para frente
            reversePr=[0.0],  # Probabilidade reversa 0
            hasIntermediate=False,
        )

    @pytest.fixture
    def processor(self, simple_reaction: Reaction) -> ReactionProcessor:
        """Instância do ReactionProcessor usando a reação simples"""
        return ReactionProcessor([simple_reaction])

    @pytest.fixture
    def small_matrix(self) -> np.ndarray:
        """Matriz 2×2 com A (1) e B (2) adjacentes na primeira linha"""
        # 0 = vazio, 1 = A, 2 = B
        return np.array([[1, 2], [0, 0]], dtype=np.int16)

    @pytest.fixture
    def identity_constraint_checker(self):
        """Constraint checker que apenas verifica limites da matriz."""

        def checker(surface_type: SurfaceTypes, row: int, col: int):  # noqa: D401
            if 0 <= row < 2 and 0 <= col < 2:
                return (row, col)
            return None  # Fora dos limites – ignora

        return checker

    # ------------------------------------------------------------------
    # Teste 1 – find_possible_reactions retorna candidatos corretos
    # ------------------------------------------------------------------

    def test_find_possible_reactions_simple_case(
        self,
        processor: ReactionProcessor,
        small_matrix: np.ndarray,
        identity_constraint_checker,
    ):
        """Verifica se a função detecta corretamente a reação A+B → C+D."""

        position = (0, 0)  # Componente A
        component = get_component_index("A")  # 1
        state = SimulationState()

        possible = processor.find_possible_reactions(
            small_matrix,
            position,
            component,
            SurfaceTypes.Torus,
            identity_constraint_checker,
            state,
        )

        # Deve existir apenas um candidato
        assert len(possible) == 1
        candidate: ReactionCandidate = possible[0]

        # Índice 0 porque é a primeira combinação encontrada
        assert candidate.index == 0
        # Produtos correspondem a C (3) e D (4)
        assert candidate.products == [
            get_component_index("C"),
            get_component_index("D"),
        ]
        # Posições na mesma ordem da chamada (pos1 = A, pos2 = B)
        assert candidate.products_position == (position, (0, 1))
        # Probabilidade preservada
        assert candidate.reaction_probability == 1.0

    # ------------------------------------------------------------------
    # Teste 2 – select_and_execute_reaction executa e actualiza a matriz
    # ------------------------------------------------------------------

    def test_select_and_execute_reaction_success(
        self,
        processor: ReactionProcessor,
        small_matrix: np.ndarray,
        identity_constraint_checker,
    ):
        """Garante que a reação é executada e o estado é atualizado."""

        state = SimulationState()
        component = get_component_index("A")
        position = (0, 0)

        possible = processor.find_possible_reactions(
            small_matrix,
            position,
            component,
            SurfaceTypes.Torus,
            identity_constraint_checker,
            state,
        )

        # Forçamos a escolha determinística do primeiro candidato
        processor.random_generator = Mock()
        processor.random_generator.choice = Mock(side_effect=lambda arr, p: arr[0])

        executed = processor.select_and_execute_reaction(
            possible, component, small_matrix, state
        )

        assert executed is True, "A reação deveria ocorrer."
        # A e B foram transformados em C e D, respectivamente
        assert small_matrix[0, 0] == get_component_index("C")
        assert small_matrix[0, 1] == get_component_index("D")
        # Componentes marcados como reagidos
        assert (0, 0) in state.reacted_components
        assert (0, 1) in state.reacted_components

    # ------------------------------------------------------------------
    # Teste 3 – select_and_execute_reaction não executa quando prob=0
    # ------------------------------------------------------------------

    def test_select_and_execute_reaction_no_probability(
        self,
        small_matrix: np.ndarray,
    ):
        """Quando todas as probabilidades são zero, nenhuma reação deve ocorrer."""

        # Candidato artificial com probabilidade 0
        candidate = ReactionCandidate(
            index=0,
            products=[get_component_index("C"), get_component_index("D")],
            products_position=((0, 0), (0, 1)),
            reaction_probability=0.0,
        )
        processor = ReactionProcessor([])  # Sem reações registradas
        state = SimulationState()

        executed = processor.select_and_execute_reaction(
            [candidate],
            get_component_index("A"),
            small_matrix,
            state,
        )

        # A matriz permanece inalterada
        assert executed is False
        assert small_matrix[0, 0] == get_component_index("A")
        assert small_matrix[0, 1] == get_component_index("B")
        # Componentes marcados como "não reagidos"
        assert (0, 0) in state.not_reacted_components
        assert (0, 1) in state.not_reacted_components
