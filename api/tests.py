from calculations import Calculations
from schemas import PairParameter
from utils import get_component_index


def test_calculate_cell_counts():
    assert Calculations.calculate_cell_counts(150, [60, 30, 10]) == [90, 45, 15]
    assert Calculations.calculate_cell_counts(473, [47.3, 52.7]) == [224, 249]


def test_calculate_pbs():
    # Mock the get_component_index function
    def mock_get_component_index(name):
        return {"A": 0, "B": 1, "C": 2}.get(name, -1)

    # Replace the original function with the mock
    original_get_component_index = get_component_index
    Calculations.get_component_index = mock_get_component_index

    try:
        # Test case 1: Single pair parameter
        pair_parameters = [PairParameter(relation=("A", "B"), value=1.0)]
        expected_result = {(0, 1): 0.6}
        assert Calculations.calculate_pbs(pair_parameters) == expected_result

        # Test case 2: Multiple pair parameters
        pair_parameters = [
            PairParameter(relation=("A", "B"), value=1.0),
            PairParameter(relation=("B", "C"), value=2.0),
        ]
        expected_result = {
            (0, 1): 0.6,
            (1, 2): 0.42857142857142855,
        }
        assert Calculations.calculate_pbs(pair_parameters) == expected_result

        # Test case 3: No pair parameters
        pair_parameters = []
        expected_result = {}
        assert Calculations.calculate_pbs(pair_parameters) == expected_result

    finally:
        # Restore the original function
        Calculations.get_component_index = original_get_component_index
