import sys
from pathlib import Path

from api.services.simulation_state import SimulationState
import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))

from utils import calculate_cell_counts
from services.calculations_helper import SurfaceTypes, calculate_pbs
from services.cellular_automata_calculator import CellularAutomataCalculator
from services.movement_analyzer import MovementAnalyzer
from services.reaction_processor import ReactionProcessor
from services.rotation_manager import RotationManager
from api.domain.schemas import (
    Ingredient,
    PairParameter,
    Parameters,
    Reaction,
    Rotation,
    SimulationBase,
)


@pytest.fixture
def mock_get_component_index(monkeypatch):
    def mock_function(name):
        return {"A": 0, "B": 1, "C": 2}.get(name, -1)

    monkeypatch.setattr("utils.get_component_index", mock_function)


def test_calculate_cell_counts():
    assert calculate_cell_counts(150, [60, 30, 10]) == [
        90,
        45,
        15,
    ]
    assert calculate_cell_counts(473, [47.3, 52.7]) == [
        224,
        249,
    ]


@pytest.mark.usefixtures("mock_get_component_index")
def test_calculate_pbs():
    # Test case 1: Single pair parameter
    pair_parameters = [PairParameter(relation="A|B", value=1.0)]
    expected_result = {"A|B": 0.6}
    assert calculate_pbs(pair_parameters) == expected_result

    # Test case 2: Multiple pair parameters
    pair_parameters = [
        PairParameter(relation="A|B", value=1.0),
        PairParameter(relation="B|C", value=2.0),
    ]
    expected_result = {
        "A|B": 0.6,
        "B|C": 0.42857142857142855,
    }
    assert calculate_pbs(pair_parameters) == expected_result

    # Test case 3: No pair parameters
    pair_parameters = []
    expected_result = {}
    assert calculate_pbs(pair_parameters) == expected_result


@pytest.mark.asyncio
async def test_assert_iterations():
    # Arrange
    ingredients = [
        Ingredient(name="A", molarFraction=50, color="blue"),
        Ingredient(name="B", molarFraction=50, color="red"),
        Ingredient(name="C", molarFraction=0.0, color="green"),
    ]
    parameters = Parameters(
        Pm=[0.7, 0.7, 0.7],
        J=[
            {"relation": "A|A", "value": 0.9},
            {"relation": "A|B", "value": 0.8},
            {"relation": "A|C", "value": 0.7},
            {"relation": "B|B", "value": 0.5},
            {"relation": "B|C", "value": 0.4},
            {"relation": "C|C", "value": 0.1},
        ],
    )
    reactions = [
        Reaction(
            reactants=["A", "B"],
            products=["A", "C"],
            Pr=[0.7, 0.9],
            reversePr=[0.3, 0.1],
            hasIntermediate=True,
        )
    ]
    simulation = SimulationBase(
        name="Test Simulation",
        iterationsNumber=1000,
        gridHeight=20,
        gridLenght=20,
        ingredients=ingredients,
        parameters=parameters.model_dump(),
        reactions=reactions,
        rotation=Rotation(component="A", Prot=0.8),
    )

    # Act
    rotation_manager = RotationManager(simulation.rotation)
    movement_analyzer = MovementAnalyzer("A", rotation_manager, parameters)
    reaction_processor = ReactionProcessor(reactions)
    calculator = CellularAutomataCalculator(
        simulation=simulation,
        movement_analyzer=movement_analyzer,
        reaction_processor=reaction_processor,
        rotation_manager=rotation_manager,
        simulation_state=SimulationState(),
    )
    async for _ in calculator.calculate_cellular_automata():
        pass
    iterations = calculator.M_iter

    # Assert
    assert iterations.ndim == 3

    for i in range(1, simulation.iterationsNumber + 1):
        # Check if the number of empty cells keeps constant
        grid = iterations[i]
        assert len(grid[grid == 0]) == calculator.NEMPTY
        for j in range(simulation.gridHeight):
            for k in range(simulation.gridLenght):
                # If current cell is an intermediate, check if there is at least one intermediate in its inner neighborhood
                if iterations[i][j][k] > 100:
                    # Check the inner neighborhood (4 surrounding cells)
                    neighbors_cells = [
                        (i, j - 1, k),
                        (i, j + 1, k),
                        (i, j, k - 1),
                        (i, j, k + 1),
                    ]
                    neighbors_components = []
                    for neighbor in neighbors_cells:
                        if calculator.check_constraints(
                            SurfaceTypes.Box, neighbor[1], neighbor[2]
                        ):
                            neighbors_components.append(iterations[neighbor])

                    assert any(neighbor > 100 for neighbor in neighbors_components)


@pytest.mark.parametrize(
    "surface_type, r, c, expected",
    [
        (SurfaceTypes.Box, 5, 5, (5, 5)),  # Inside grid
        (SurfaceTypes.Box, -1, 5, None),  # Outside grid (negative row)
        (SurfaceTypes.Box, 5, -1, None),  # Outside grid (negative column)
        (SurfaceTypes.Box, 100, 5, None),  # Outside grid (row exceeds limit)
        (SurfaceTypes.Box, 5, 100, None),  # Outside grid (column exceeds limit)
        (SurfaceTypes.Cylinder, 5, 5, (5, 5)),  # Inside grid
        (SurfaceTypes.Cylinder, -1, 5, None),  # Outside grid (negative row)
        (SurfaceTypes.Cylinder, 100, 5, None),  # Outside grid (row exceeds limit)
        (SurfaceTypes.Cylinder, 5, -1, (5, 49)),  # Cylinder allows wrapping columns
        (SurfaceTypes.Cylinder, 5, 100, (5, 0)),  # Cylinder allows wrapping columns
        (SurfaceTypes.Torus, -1, -1, (49, 49)),
        (SurfaceTypes.Torus, -2, 10, (48, 10)),
        (SurfaceTypes.Torus, 6, 43, (6, 43)),
    ],
)
def test_check_constraints(surface_type, r, c, expected):
    # Arrange
    ingredients = [
        Ingredient(name="A", molarFraction=50, color="blue"),
        Ingredient(name="B", molarFraction=50, color="red"),
        Ingredient(name="C", molarFraction=0.0, color="green"),
    ]
    parameters = Parameters(
        Pm=[0.7, 0.7, 0.7],
        J=[
            {"relation": "A|A", "value": 0.9},
            {"relation": "A|B", "value": 0.8},
            {"relation": "A|C", "value": 0.7},
            {"relation": "B|B", "value": 0.5},
            {"relation": "B|C", "value": 0.4},
            {"relation": "C|C", "value": 0.1},
        ],
    )
    reactions = [
        Reaction(
            reactants=["A", "B"],
            products=["A", "C"],
            Pr=[0.7, 0.9],
            reversePr=[0.3, 0.1],
            hasIntermediate=True,
        )
    ]
    simulation = SimulationBase(
        name="Test Simulation",
        iterationsNumber=1000,
        gridHeight=50,
        gridLenght=50,
        ingredients=ingredients,
        parameters=parameters.model_dump(),
        reactions=reactions,
        rotation=Rotation(component="A", Prot=0.8),
    )

    # Act
    rotation_manager = RotationManager(simulation.rotation)
    movement_analyzer = MovementAnalyzer("A", rotation_manager, parameters)
    reaction_processor = ReactionProcessor(reactions)
    calculator = CellularAutomataCalculator(
        simulation=simulation,
        movement_analyzer=movement_analyzer,
        reaction_processor=reaction_processor,
        rotation_manager=rotation_manager,
        simulation_state=SimulationState(),
    )
    calculator._initialize_simulation()
    assert calculator.check_constraints(surface_type, r, c) == expected
