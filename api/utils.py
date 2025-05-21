import base64
import csv
import gzip
import io
import json


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
        matrix (list): A 2D list (matrix) to be compressed.
    Returns:
        str: The compressed and encoded matrix as a string.
    """
    json_bytes = json.dumps(matrix).encode("utf-8")
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
