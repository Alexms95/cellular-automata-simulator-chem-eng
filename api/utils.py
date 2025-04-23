import base64
import gzip
import json


def get_component_index(char: str) -> int:
    return ord(char) - 64


def compress_matrix(matrix: list) -> str:
    json_bytes = json.dumps(matrix).encode("utf-8")
    return base64.b64encode(gzip.compress(json_bytes)).decode("utf-8")


def decompress_matrix(data_str: str) -> list:
    return json.loads(gzip.decompress(base64.b64decode(data_str.encode())))
