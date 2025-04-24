import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent))

from calculations import Calculations
from schemas import PairParameter

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
