import base64
import csv
import gzip
import io
import json
from math import floor


def get_component_index(char: str) -> int:
    """Convert a letter to its corresponding index (A=1, B=2, ..., Z=26)
    Args:
        char (str): A single uppercase letter.
        Returns:
        int: The index of the letter (1-26).
    """
    return ord(char) - 64

def get_component_letter(index: int) -> str:
    """Convert an index (1-26) to its corresponding letter (A=1, B=2, ..., Z=26)
    Args:
        index (int): An index between 1 and 26.
    Returns:
        str: The corresponding uppercase letter.
    """
    return chr(index + 64)

def compress_matrix(matrix: list) -> str:
    """Compress a matrix using gzip and encode it with base64.
    Args:
        matrix (list): A 3D list (matrix) to be compressed.
    Returns:
        str: The compressed and encoded matrix as a string.
    """
    print(matrix)
    json_bytes = json.dumps(matrix).encode("utf-8")
    print(json.dumps(matrix))
    print(json_bytes)
    print(gzip.compress(json_bytes))
    print(base64.b64encode(gzip.compress(json_bytes)))
    print(base64.b64encode(gzip.compress(json_bytes)).decode("utf-8"))
    print("Compressed and encoded matrix:", base64.b64encode(gzip.compress(json_bytes)).decode("utf-8"))
    return base64.b64encode(gzip.compress(json_bytes)).decode("utf-8")


def decompress_matrix(data_str: str) -> list:
    """Decompress a base64 encoded gzip string back to a matrix.
    Args:
        data_str (str): A base64 encoded gzip string.
    Returns:
        list: The decompressed matrix.
    """
    return json.loads(gzip.decompress(base64.b64decode(data_str.encode())))

def convert_to_csv(data: list[list]) -> str:
    """Convert a 2D list to a CSV string.
    Args:
        data (list[list]): A 2D list to be converted to CSV.
    Returns:
        str: The CSV representation of the data.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data)
    return output.getvalue()


def calculate_cell_counts(total: int, percentages: list[float]) -> list[int]:
    """
    Calculate the number of cells for each component based on their molar fractions.
    The function takes the total number of cells and a list of percentages, and returns a list of cell counts for each component.
    The function ensures that the total number of cells is preserved by rounding the fractional counts and adjusting them if necessary.
    Args:
        total (int): The total number of cells.
        percentages (list[float]): A list of percentages representing the molar fractions of each component.
    Returns:
        list[int]: A list of cell counts for each component.
    """
    fractional_counts = [percentage * total / 100 for percentage in percentages]

    rounded_counts = [floor(fraction) for fraction in fractional_counts]

    error = abs(sum(fractional_counts) - sum(rounded_counts))

    if error == 0:
        return rounded_counts

    adjustment_list = [
        {"index": index, "difference": fraction - rounded_count}
        for index, (fraction, rounded_count) in enumerate(
            zip(fractional_counts, rounded_counts)
        )
    ]

    adjustment_list.sort(key=lambda x: x["difference"], reverse=True)

    for i in range(round(error)):
        rounded_counts[adjustment_list[i]["index"]] += 1

    return rounded_counts
