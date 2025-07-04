import pytest
import sys
import os

# Adiciona o diretório api ao path para importações
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Teste simples para verificar se as importações estão funcionando"""
    try:
        from services.movement_analyzer import MovementAnalyzer
        from domain.schemas import Parameters, PairParameter
        assert True
    except ImportError as e:
        pytest.fail(f"Erro de importação: {e}")

if __name__ == "__main__":
    test_imports()
    print("Importações funcionando corretamente!")