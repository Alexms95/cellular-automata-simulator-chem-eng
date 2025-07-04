import sys
from pathlib import Path
from typing import List, Tuple
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

# Adiciona o diretório atual ao path para importações
sys.path.append(str(Path(__file__).resolve().parent.parent))

from domain.schemas import PairParameter, Parameters, Rotation
from services.calculations_helper import SurfaceTypes
from services.movement_analyzer import MovementAnalyzer
from services.rotation_manager import RotationManager


class TestMovementAnalyzer:
    """Testes unitários para a classe MovementAnalyzer"""

    @pytest.fixture
    def sample_parameters(self):
        """Fixture com parâmetros de exemplo para os testes"""
        return Parameters(
            Pm=[0.5, 0.3, 0.7],  # Probabilidades de movimento para componentes 1, 2, 3
            J=[
                PairParameter(relation="A|B", value=2.0),
                PairParameter(relation="B|C", value=1.5),
                PairParameter(relation="A|C", value=0.5),
                PairParameter(relation="R1|A", value=3.0),
                PairParameter(relation="R2|B", value=2.5),
            ],
        )

    @pytest.fixture
    def sample_rotation(self):
        """Fixture com configuração de rotação de exemplo"""
        return Rotation(component="R", Prot=0.8)

    @pytest.fixture
    def mock_rotation_manager(self, sample_rotation):
        """Fixture com RotationManager mockado"""
        mock_manager = Mock(spec=RotationManager)
        mock_manager.get_rotation_info.return_value = {
            "component": 1,
            "states": [11, 12, 13, 14],  # Estados de rotação
            "p_rot": 0.8,
        }
        return mock_manager

    @pytest.fixture
    def movement_analyzer(self, sample_parameters, mock_rotation_manager):
        """Fixture com MovementAnalyzer configurado"""
        return MovementAnalyzer(
            rotation_component="R",
            rotation_manager=mock_rotation_manager,
            parameters=sample_parameters,
        )

    @pytest.fixture
    def sample_matrix(self):
        """Fixture com matriz de exemplo para testes"""
        return np.array([[0, 1, 0, 2], [1, 0, 2, 0], [0, 2, 0, 1], [2, 0, 1, 0]])

    @pytest.fixture
    def mock_constraint_checker(self):
        """Fixture com constraint_checker mockado"""

        def constraint_checker(surface_type, row, col):
            # Simula validação de coordenadas dentro dos limites
            if 0 <= row < 4 and 0 <= col < 4:
                return (row, col)
            return None

        return constraint_checker

    def test_init(self, sample_parameters, mock_rotation_manager):
        """Testa a inicialização da classe MovementAnalyzer"""
        analyzer = MovementAnalyzer("R", mock_rotation_manager, sample_parameters)

        assert analyzer.rotation_component == "R"
        assert analyzer.parameters == sample_parameters
        assert analyzer.rotation_info == mock_rotation_manager.get_rotation_info()
        assert len(analyzer.pbs) > 0  # PBS calculados
        assert analyzer.random_generator is not None

    def test_analyze_movement_possibility_basic(
        self, movement_analyzer, sample_matrix, mock_constraint_checker
    ):
        """Testa análise básica de movimento"""
        position = (1, 1)  # Posição vazia na matriz
        component = 1
        surface_type = SurfaceTypes.Torus

        result = movement_analyzer.analyze_movement_possibility(
            sample_matrix, position, component, surface_type, mock_constraint_checker
        )

        assert isinstance(result, tuple)
        assert len(result) == 3
        can_move, target_position, probability = result

        assert isinstance(can_move, bool)
        assert isinstance(probability, float)
        assert 0 <= probability <= 1

        if can_move:
            assert target_position is not None
            assert isinstance(target_position, tuple)
            assert len(target_position) == 2

    def test_calculate_j_neighbors(
        self, movement_analyzer, sample_matrix, mock_constraint_checker
    ):
        """Testa cálculo de vizinhos J"""
        position = (1, 1)
        component = 1
        surface_type = SurfaceTypes.Torus

        inner_neighbors = np.array([[-1, 0], [0, -1], [1, 0], [0, 1]]) + np.array(
            position
        )
        outer_neighbors = 2 * np.array([[-1, 0], [0, -1], [1, 0], [0, 1]]) + np.array(
            position
        )

        j_neighbors = movement_analyzer._calculate_j_neighbors(
            sample_matrix,
            inner_neighbors,
            outer_neighbors,
            component,
            surface_type,
            mock_constraint_checker,
        )

        assert isinstance(j_neighbors, list)
        for neighbor in j_neighbors:
            assert isinstance(neighbor, tuple)
            assert len(neighbor) == 2
            assert isinstance(neighbor[0], int)  # índice da posição
            assert isinstance(neighbor[1], float)  # valor J

    def test_find_j_value_for_pair_existing(self, movement_analyzer):
        """Testa busca de valor J para par existente"""
        comp1 = "A"
        comp2 = "B"

        j_value = movement_analyzer._find_j_value_for_pair(comp1, comp2)

        assert isinstance(j_value, float)
        assert j_value == 2.0  # Valor definido nos parâmetros de exemplo

    def test_find_j_value_for_pair_nonexistent(self, movement_analyzer):
        """Testa busca de valor J para par inexistente"""
        comp1 = "X"
        comp2 = "Y"

        j_value = movement_analyzer._find_j_value_for_pair(comp1, comp2)

        assert j_value == 0.0

    def test_select_target_neighbor_empty_list(self, movement_analyzer):
        """Testa seleção de vizinho alvo com lista vazia"""
        j_neighbors = []

        target = movement_analyzer._select_target_neighbor(j_neighbors)

        assert target is None

    def test_select_target_neighbor_with_values(self, movement_analyzer):
        """Testa seleção de vizinho alvo com valores"""
        j_neighbors = [(0, 0.5), (1, 1.5), (2, 1.0)]

        target = movement_analyzer._select_target_neighbor(j_neighbors)

        assert target is not None
        import numpy as np
        assert isinstance(target, (tuple, np.ndarray))
        assert len(target) == 2

    def test_get_component_representation_normal(self, movement_analyzer):
        """Testa representação de componente normal"""
        component = 1
        direction = 0

        representation = movement_analyzer._get_component_representation(
            component, direction
        )

        assert representation == "A"

    def test_calculate_movement_probability_no_neighbors(self, movement_analyzer):
        """Testa cálculo de probabilidade sem vizinhos ocupados"""
        component = 1
        occupied_neighbors = []
        matrix = np.zeros((3, 3))

        probability = movement_analyzer._calculate_movement_probability(
            component, occupied_neighbors, matrix
        )

        assert isinstance(probability, float)
        assert probability == 0.5  # Pm[0] do parâmetro de exemplo

    def test_get_occupied_inner_neighbors(
        self, movement_analyzer, sample_matrix, mock_constraint_checker
    ):
        """Testa obtenção de vizinhos internos ocupados"""
        inner_neighbors = np.array([[0, 1], [1, 0], [2, 1], [1, 2]])
        surface_type = SurfaceTypes.Torus

        occupied = movement_analyzer._get_occupied_inner_neighbors(
            sample_matrix, inner_neighbors, surface_type, mock_constraint_checker
        )

        assert isinstance(occupied, list)
        for item in occupied:
            assert isinstance(item, tuple)
            assert len(item) == 3  # (índice, linha, coluna)

    @pytest.mark.parametrize(
        "surface_type", [SurfaceTypes.Torus, SurfaceTypes.Cylinder, SurfaceTypes.Box]
    )
    def test_different_surface_types(
        self, movement_analyzer, sample_matrix, surface_type
    ):
        """Testa análise com diferentes tipos de superfície"""
        position = (1, 1)
        component = 1

        def constraint_checker(surf_type, row, col):
            if surf_type == SurfaceTypes.Box:
                if 0 <= row < 4 and 0 <= col < 4:
                    return (row, col)
                return None
            else:
                return (row % 4, col % 4)

        result = movement_analyzer.analyze_movement_possibility(
            sample_matrix, position, component, surface_type, constraint_checker
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_edge_case_small_matrix(self, movement_analyzer):
        """Testa casos extremos com matriz pequena"""
        small_matrix = np.array([[1, 0], [0, 2]])

        def small_constraint_checker(surface_type, row, col):
            if 0 <= row < 2 and 0 <= col < 2:
                return (row, col)
            return None

        position = (0, 0)
        component = 1
        surface_type = SurfaceTypes.Box

        result = movement_analyzer.analyze_movement_possibility(
            small_matrix, position, component, surface_type, small_constraint_checker
        )

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_component_pair_interaction_normal(self, movement_analyzer):
        """Testa interação entre componentes normais"""
        component1 = 1  # Componente A
        component2 = 2  # Componente B
        direction = 0

        comp1, comp2 = movement_analyzer._get_component_pair_for_interaction(
            component1, component2, direction
        )

        assert isinstance(comp1, str)
        assert isinstance(comp2, str)
        assert comp1 == "A"
        assert comp2 == "B"

    def test_movement_probability_with_neighbors(
        self, movement_analyzer, sample_matrix
    ):
        """Testa cálculo de probabilidade com vizinhos ocupados"""
        component = 1
        occupied_neighbors = [(0, 0, 1), (1, 1, 0)]  # Vizinhos ocupados

        probability = movement_analyzer._calculate_movement_probability(
            component, occupied_neighbors, sample_matrix
        )

        assert isinstance(probability, float)
        assert 0.0 <= probability <= 1.0

    def test_j_value_calculation_for_position(
        self, movement_analyzer, sample_matrix, mock_constraint_checker
    ):
        """Testa cálculo do valor J para posição específica"""
        component = 1
        position_index = 0
        outer_neighbors = np.array([[0, 1], [1, 0], [2, 1], [1, 2]])
        surface_type = SurfaceTypes.Torus

        j_value = movement_analyzer._calculate_j_value_for_position(
            sample_matrix,
            component,
            position_index,
            outer_neighbors,
            surface_type,
            mock_constraint_checker,
        )

        assert isinstance(j_value, float)
        assert j_value >= 0.0
