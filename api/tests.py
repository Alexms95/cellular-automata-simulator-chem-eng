from api.calculations import calculate_cell_counts

def test_calculate_cell_counts():
  assert calculate_cell_counts(150, [60, 30, 10]) == [90, 45, 15]
  assert calculate_cell_counts(473, [47.3, 52.7]) == [224, 249]