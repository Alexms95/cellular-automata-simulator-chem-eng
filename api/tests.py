import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent))

from calculations import Calculations, SurfaceTypes
from schemas import Ingredient, PairParameter, Parameters, Reaction, SimulationBase


@pytest.fixture
def mock_get_component_index(monkeypatch):
    def mock_function(name):
        return {"A": 0, "B": 1, "C": 2}.get(name, -1)

    monkeypatch.setattr("utils.get_component_index", mock_function)


def test_calculate_cell_counts():
    assert Calculations.calculate_cell_counts(150, [60, 30, 10]) == [90, 45, 15]
    assert Calculations.calculate_cell_counts(473, [47.3, 52.7]) == [224, 249]


@pytest.mark.usefixtures("mock_get_component_index")
def test_calculate_pbs():
    # Test case 1: Single pair parameter
    pair_parameters = [PairParameter(relation="AB", value=1.0)]
    expected_result = {(1, 2): 0.6}
    assert Calculations.calculate_pbs(pair_parameters) == expected_result

    # Test case 2: Multiple pair parameters
    pair_parameters = [
        PairParameter(relation="AB", value=1.0),
        PairParameter(relation="BC", value=2.0),
    ]
    expected_result = {
        (1, 2): 0.6,
        (2, 3): 0.42857142857142855,
    }
    assert Calculations.calculate_pbs(pair_parameters) == expected_result

    # Test case 3: No pair parameters
    pair_parameters = []
    expected_result = {}
    assert Calculations.calculate_pbs(pair_parameters) == expected_result


def test_assert_iterations():
    # Arrange
    ingredients = [
        Ingredient(name="A", molarFraction=50, color="blue"),
        Ingredient(name="B", molarFraction=50, color="red"),
        Ingredient(name="C", molarFraction=0.0, color="green"),
    ]
    parameters = Parameters(
        Pm=[0.7, 0.7, 0.7],
        J=[
            {"relation": "AA", "value": 0.9},
            {"relation": "AB", "value": 0.8},
            {"relation": "AC", "value": 0.7},
            {"relation": "BB", "value": 0.5},
            {"relation": "BC", "value": 0.4},
            {"relation": "CC", "value": 0.1},
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
    )

    # Act
    iterations = Calculations.calculate_cellular_automata(simulation)

    # Assert
    assert iterations.ndim == 3

    for i in range(1, simulation.iterationsNumber + 1):
        # Check if the number of empty cells keeps constant
        grid = iterations[i]
        assert len(grid[grid == 0]) == Calculations.NEMPTY
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
                        if Calculations.check_constraints(
                            SurfaceTypes.Box, neighbor[1], neighbor[2]
                        ):
                            neighbors_components.append(iterations[neighbor])

                    assert any(neighbor > 100 for neighbor in neighbors_components)


@pytest.mark.parametrize(
    "surface_type, r, c, expected",
    [
        (SurfaceTypes.Box, 5, 5, True),  # Inside grid
        (SurfaceTypes.Box, -1, 5, False),  # Outside grid (negative row)
        (SurfaceTypes.Box, 5, -1, False),  # Outside grid (negative column)
        (SurfaceTypes.Box, 100, 5, False),  # Outside grid (row exceeds limit)
        (SurfaceTypes.Box, 5, 100, False),  # Outside grid (column exceeds limit)
        (SurfaceTypes.Cylinder, 5, 5, True),  # Inside grid
        (SurfaceTypes.Cylinder, -1, 5, False),  # Outside grid (negative row)
        (SurfaceTypes.Cylinder, 100, 5, False),  # Outside grid (row exceeds limit)
        (SurfaceTypes.Cylinder, 5, -1, True),  # Cylinder allows wrapping columns
        (SurfaceTypes.Cylinder, 5, 100, True),  # Cylinder allows wrapping columns
    ],
)
def test_check_constraints(surface_type, r, c, expected):
    Calculations.NL = 50  # Set grid height
    Calculations.NC = 50  # Set grid length
    assert Calculations.check_constraints(surface_type, r, c) == expected
