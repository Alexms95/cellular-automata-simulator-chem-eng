from app.schemas.calculation_schema import CalculationInput, CalculationResult

class CalculationController:
    def add(self, calculation: CalculationInput) -> CalculationResult:
        result = calculation.a + calculation.b
        return CalculationResult(result=result)

    def subtract(self, calculation: CalculationInput) -> CalculationResult:
        result = calculation.a - calculation.b
        return CalculationResult(result=result)
