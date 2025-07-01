import sys
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest

# Allow running the tests directly with "pytest -q" from project root
sys.path.append(str(Path(__file__).resolve().parent.parent))

from domain.schemas import (
    Ingredient,
    PairParameter,
    Parameters,
    Reaction,
    Rotation,
    SimulationBase,
)
from services.calculations_helper import SurfaceTypes, is_component
from services.cellular_automata_calculator import CellularAutomataCalculator
from services.movement_analyzer import MovementAnalyzer
from services.reaction_processor import ReactionProcessor
from services.rotation_manager import RotationManager
from services.simulation_state import SimulationState


class TestCellularAutomataCalculator:
    """Testes unitários para a classe CellularAutomataCalculator"""

    # ------------------------------------------------------------------
    # FIXTURES BÁSICOS --------------------------------------------------
    # ------------------------------------------------------------------
    @pytest.fixture
    def sample_simulation(self) -> SimulationBase:
        """Retorna uma configuração mínima porém consistente de simulação."""
        ingredients: List[Ingredient] = [
            Ingredient(name="A", molarFraction=40.0, color="#FF0000"),
            Ingredient(name="B", molarFraction=60.0, color="#00FF00"),
        ]
        parameters = Parameters(Pm=[0.5, 0.5], J=[])
        rotation = Rotation(component="R", Prot=0.0)  # sem rotação para simplificar
        return SimulationBase(
            name="unit-test-sim",
            iterationsNumber=5,
            gridLenght=4,
            gridHeight=4,
            ingredients=ingredients,
            parameters=parameters,
            reactions=None,
            rotation=rotation,
        )

    @pytest.fixture
    def dummy_services(self):
        """Cria mocks para os serviços dependentes usados pelo calculator."""
        # Mock MovementAnalyzer – nunca permitirá movimento
        movement_analyzer = MagicMock(spec=MovementAnalyzer)
        movement_analyzer.analyze_movement_possibility.return_value = (False, None, 0.0)

        # Mock ReactionProcessor – nunca há reações
        reaction_processor = MagicMock(spec=ReactionProcessor)
        reaction_processor.find_possible_reactions.return_value = []
        reaction_processor.select_and_execute_reaction.return_value = False

        # Mock RotationManager – sem rotação, apenas info vazia
        rotation_manager = MagicMock(spec=RotationManager)
        rotation_manager.get_rotation_info.return_value = {
            "component": None,
            "states": [],
            "p_rot": 0.0,
        }

        # Estado da simulação real (não precisa mock)
        simulation_state = SimulationState()

        return movement_analyzer, reaction_processor, rotation_manager, simulation_state

    @pytest.fixture
    def calculator(self, sample_simulation, dummy_services):
        """Instância do CellularAutomataCalculator com dependências mockadas."""
        movement_analyzer, reaction_processor, rotation_manager, simulation_state = (
            dummy_services
        )
        calc = CellularAutomataCalculator(
            simulation=sample_simulation,
            movement_analyzer=movement_analyzer,
            reaction_processor=reaction_processor,
            rotation_manager=rotation_manager,
            simulation_state=simulation_state,
            surface_type=SurfaceTypes.Torus,  # tipo padrão
        )
        return calc

    # ------------------------------------------------------------------
    # TESTES ------------------------------------------------------------
    # ------------------------------------------------------------------
    def test_initialize_simulation(self, calculator, sample_simulation):
        """Testa se a inicialização gera matriz com dimensões corretas e sem buracos no total de células ocupadas."""
        # Fixar semente para resultados determinísticos
        np.random.seed(0)

        matrix = calculator._initialize_simulation()

        # Dimensões corretas
        assert matrix.shape == (
            sample_simulation.gridHeight,
            sample_simulation.gridLenght,
        )

        # Total de células não vazias = NCELL
        non_zero = np.count_nonzero(matrix)
        assert (
            non_zero
            == calculator.NCELL
            == sample_simulation.gridHeight * sample_simulation.gridLenght
            - calculator.NEMPTY
        )

        # Todos os valores de componentes devem ser 0 ou pertencentes a um ingrediente
        allowed = {0, 1, 2}  # índices dos componentes (1-based)
        assert set(np.unique(matrix)).issubset(allowed)

    def test_calculate_cellular_automata_progress_and_results(
        self, calculator, sample_simulation
    ):
        """Executa a simulação assíncrona usando asyncio.run e verifica resultados."""
        import asyncio

        np.random.seed(1)  # nova semente para caminho diferente

        async def _run():
            progresses: list = []
            async for prog in calculator.calculate_cellular_automata():
                progresses.append(prog)
            return progresses

        progresses = asyncio.run(_run())

        # Como iterationsNumber=5 (<10), somente a última atualização deve ser emitida
        assert progresses == [
            (sample_simulation.iterationsNumber, sample_simulation.iterationsNumber)
        ]

        # Após execução, get_results deve ter shape (n_iter+1, linhas, colunas)
        matrices, molar_table = calculator.get_results()
        expected_shape = (
            sample_simulation.iterationsNumber + 1,
            sample_simulation.gridHeight,
            sample_simulation.gridLenght,
        )
        assert matrices.shape == expected_shape

        # A primeira fatia (iteração 0) deve estar presente e conter componentes válidos
        assert np.count_nonzero(matrices[0]) > 0
        assert (
            len(molar_table) == sample_simulation.iterationsNumber + 2
        )  # header + n_iter+1 linhas

    @pytest.mark.parametrize(
        "surface_type, input_pos",
        [
            (SurfaceTypes.Torus, (-1, -1)),  # Deve envolver índices
            (SurfaceTypes.Cylinder, (-1, 2)),  # Linha fora do limite → None
            (SurfaceTypes.Box, (10, 10)),  # Fora do limite → None
        ],
    )
    def test_check_constraints(self, calculator, surface_type, input_pos):
        """Verifica se a verificação de restrições funciona para diferentes superfícies."""
        # Precisamos inicializar NL e NC
        calculator.NL = 4
        calculator.NC = 4

        r, c = input_pos
        result = calculator.check_constraints(surface_type, r, c)

        if surface_type == SurfaceTypes.Torus:
            # No toro, índices devem ser envolvidos pelos limites (método modular)
            assert result == ((r % calculator.NL), (c % calculator.NC))
        elif surface_type == SurfaceTypes.Cylinder:
            # Para cilindro, somente colunas envolvem; linha fora → None
            if 0 <= r < calculator.NL:
                assert result == (r, c % calculator.NC)
            else:
                assert result is None
        else:  # SurfaceTypes.Box
            if 0 <= r < calculator.NL and 0 <= c < calculator.NC:
                assert result == (r, c)
            else:
                assert result is None

    
