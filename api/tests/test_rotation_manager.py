import sys
from pathlib import Path
from typing import Tuple
from unittest.mock import Mock, patch

import numpy as np
import pytest

# Adiciona o diretório atual ao path para importações
sys.path.append(str(Path(__file__).resolve().parent.parent))

from domain.schemas import Rotation, RotationInfo
from services.calculations_helper import SurfaceTypes
from services.rotation_manager import RotationManager


class TestRotationManager:
    """Testes unitários para a classe RotationManager"""

    @pytest.fixture
    def rotation_without_component(self):
        """Fixture com rotação sem componente definido"""
        return Rotation(component="None", Prot=0.0)

    @pytest.fixture
    def rotation_with_component_a(self):
        """Fixture com rotação para componente A"""
        return Rotation(component="A", Prot=0.8)

    @pytest.fixture
    def rotation_with_component_r(self):
        """Fixture com rotação para componente R"""
        return Rotation(component="R", Prot=0.5)

    @pytest.fixture
    def sample_matrix(self):
        """Fixture com matriz de exemplo para testes"""
        # Matriz 5x5 com:
        # 0 = vazio
        # 1 = componente A
        # 2 = componente B
        # 11-14 = estados de rotação do componente A
        return np.array(
            [
                [0, 1, 0, 2, 0],
                [1, 11, 0, 0, 1],
                [0, 0, 12, 0, 0],
                [2, 0, 0, 13, 0],
                [0, 1, 0, 0, 14],
            ]
        )

    @pytest.fixture
    def mock_constraint_checker(self):
        """Mock para o constraint_checker que simula verificação de bordas"""

        def checker(surface_type, row, col):
            # Simula comportamento de torus - sem bordas
            if 0 <= row < 5 and 0 <= col < 5:
                return (row, col)
            # Wrap around para simular torus
            return (row % 5, col % 5)

        return checker

    def test_init_without_component(self, rotation_without_component):
        """Testa inicialização sem componente de rotação"""
        manager = RotationManager(rotation_without_component)
        rotation_info = manager.get_rotation_info()

        assert rotation_info["component"] == -1
        assert rotation_info["p_rot"] == 0
        assert rotation_info["states"] == [0]

    def test_init_with_component_a(self, rotation_with_component_a):
        """Testa inicialização com componente A"""
        manager = RotationManager(rotation_with_component_a)
        rotation_info = manager.get_rotation_info()

        # Componente A tem índice 1 (A=1, B=2, etc.)
        assert rotation_info["component"] == 1
        assert rotation_info["p_rot"] == 0.8
        # Estados de rotação para componente 1: 11, 12, 13, 14
        assert rotation_info["states"] == [11, 12, 13, 14]

    def test_init_with_component_r(self, rotation_with_component_r):
        """Testa inicialização com componente R"""
        manager = RotationManager(rotation_with_component_r)
        rotation_info = manager.get_rotation_info()

        # Componente R tem índice 18 (R é a 18ª letra)
        assert rotation_info["component"] == 18
        assert rotation_info["p_rot"] == 0.5
        # Estados de rotação para componente 18: 181, 182, 183, 184
        assert rotation_info["states"] == [181, 182, 183, 184]

    def test_can_rotate_empty_neighbors(
        self, rotation_with_component_a, sample_matrix, mock_constraint_checker
    ):
        """Testa se pode rotacionar quando todos os vizinhos estão vazios"""
        manager = RotationManager(rotation_with_component_a)

        # Posição (2, 2) tem componente 12 e todos os vizinhos vazios
        can_rotate = manager.can_rotate(
            sample_matrix, (2, 2), SurfaceTypes.Torus, mock_constraint_checker
        )

        assert can_rotate is True

    def test_cannot_rotate_with_component_neighbors(
        self, rotation_with_component_a, sample_matrix, mock_constraint_checker
    ):
        """Testa que não pode rotacionar quando há componentes vizinhos"""
        manager = RotationManager(rotation_with_component_a)

        # Posição (1, 1) tem componente 11 e tem componente 1 como vizinho
        can_rotate = manager.can_rotate(
            sample_matrix, (1, 1), SurfaceTypes.Torus, mock_constraint_checker
        )

        assert can_rotate is False

    def test_can_rotate_edge_case(
        self, rotation_with_component_a, mock_constraint_checker
    ):
        """Testa rotação em posições de borda"""
        manager = RotationManager(rotation_with_component_a)

        # Matriz com componente no canto
        matrix = np.array([[11, 0, 0], [0, 0, 0], [0, 0, 0]])

        # Mock que simula wrap-around
        def edge_checker(surface_type, row, col):
            return ((row + 3) % 3, (col + 3) % 3)

        can_rotate = manager.can_rotate(
            matrix, (0, 0), SurfaceTypes.Torus, edge_checker
        )

        assert can_rotate is True

    @patch("numpy.random.choice")
    def test_rotate_component_success(
        self, mock_choice, rotation_with_component_a, sample_matrix
    ):
        """Testa rotação bem-sucedida de um componente"""
        manager = RotationManager(rotation_with_component_a)
        mock_choice.return_value = 13  # Novo estado escolhido

        # Rotaciona componente na posição (1, 1) que tem valor 11
        manager.rotate_component(sample_matrix, (1, 1), 11)

        # Verifica que o componente foi rotacionado
        assert sample_matrix[1, 1] == 13
        # Verifica que foi chamado com os estados corretos (excluindo o atual)
        mock_choice.assert_called_once_with([12, 13, 14])

    @patch("numpy.random.choice")
    def test_rotate_component_all_states(
        self, mock_choice, rotation_with_component_a, sample_matrix
    ):
        """Testa que todos os estados de rotação são considerados exceto o atual"""
        manager = RotationManager(rotation_with_component_a)

        # Testa rotação de cada estado
        test_cases = [
            (11, [12, 13, 14]),
            (12, [11, 13, 14]),
            (13, [11, 12, 14]),
            (14, [11, 12, 13]),
        ]

        for current_state, expected_available in test_cases:
            mock_choice.reset_mock()
            mock_choice.return_value = expected_available[0]

            test_matrix = np.array([[current_state]])
            manager.rotate_component(test_matrix, (0, 0), current_state)

            mock_choice.assert_called_once_with(expected_available)

    def test_rotate_component_empty_states(self, rotation_without_component):
        """Testa comportamento quando não há estados disponíveis"""
        manager = RotationManager(rotation_without_component)
        # Modifica manualmente para ter lista vazia de estados
        manager._RotationManager__rotation_info["states"] = []

        matrix = np.array([[1]])
        manager.rotate_component(matrix, (0, 0), 1)

        # Matriz deve permanecer inalterada
        assert matrix[0, 0] == 1

    def test_get_rotation_info_immutability(self, rotation_with_component_a):
        """Testa que get_rotation_info retorna informação consistente"""
        manager = RotationManager(rotation_with_component_a)

        info1 = manager.get_rotation_info()
        info2 = manager.get_rotation_info()

        assert info1 == info2
        assert info1 is info2  # Deve retornar a mesma referência

    @pytest.mark.parametrize(
        "component,expected_index",
        [
            ("A", 1),
            ("B", 2),
            ("C", 3),
            ("Z", 26),
        ],
    )
    def test_component_index_calculation(self, component, expected_index):
        """Testa cálculo correto do índice para diferentes componentes"""
        rotation = Rotation(component=component, Prot=0.5)
        manager = RotationManager(rotation)
        rotation_info = manager.get_rotation_info()

        assert rotation_info["component"] == expected_index
        assert rotation_info["states"] == [
            expected_index * 10 + 1,
            expected_index * 10 + 2,
            expected_index * 10 + 3,
            expected_index * 10 + 4,
        ]

    def test_can_rotate_with_different_surface_types(self, rotation_with_component_a):
        """Testa can_rotate com diferentes tipos de superfície"""
        manager = RotationManager(rotation_with_component_a)

        # Matriz com espaço livre
        matrix = np.array([[0, 0, 0], [0, 11, 0], [0, 0, 0]])

        # Testa com diferentes tipos de superfície
        for surface_type in [
            SurfaceTypes.Torus,
            SurfaceTypes.Cylinder,
            SurfaceTypes.Box,
        ]:
            can_rotate = manager.can_rotate(
                matrix,
                (1, 1),
                surface_type,
                lambda st, r, c: (r, c) if 0 <= r < 3 and 0 <= c < 3 else None,
            )
            assert can_rotate is True

    def test_can_rotate_constraint_checker_returns_none(
        self, rotation_with_component_a
    ):
        """Testa comportamento quando constraint_checker retorna None"""
        manager = RotationManager(rotation_with_component_a)

        matrix = np.array([[11]])

        # Mock que retorna None para simular posição inválida
        def constraint_checker(surface_type, row, col):
            return None

        # Deve poder rotacionar pois posições inválidas são ignoradas
        can_rotate = manager.can_rotate(
            matrix, (0, 0), SurfaceTypes.Box, constraint_checker
        )

        assert can_rotate is True

    def test_rotation_probability_preserved(self, rotation_with_component_a):
        """Testa que a probabilidade de rotação é preservada corretamente"""
        manager = RotationManager(rotation_with_component_a)
        rotation_info = manager.get_rotation_info()

        assert rotation_info["p_rot"] == 0.8

    def test_empty_component_string(self):
        """Testa comportamento com string vazia como componente"""
        rotation = Rotation(component="", Prot=0.5)
        manager = RotationManager(rotation)
        rotation_info = manager.get_rotation_info()

        # String vazia deve ser tratada como sem componente
        assert rotation_info["component"] == -1
        assert rotation_info["p_rot"] == 0
        assert rotation_info["states"] == [0]
