"""
Tests para el módulo de hash calculator.
"""

from liquidator.audit.hash_calculator import HashCalculator, calculate_hash


class TestHashCalculatorModule:
    """Tests para la función module-level calculate_hash."""

    def test_calculate_hash_returns_sha256_prefix(self):
        """Test que calculate_hash retorna prefijo sha256:."""
        test_dict = {"field1": "value1"}
        hash_result = calculate_hash(test_dict)
        assert hash_result.startswith("sha256:")
        assert len(hash_result) == 71  # sha256: + 64 hex chars

    def test_calculate_hash_deterministic(self):
        """Test que el hash de dict es determinístico."""
        test_dict1 = {
            "field1": "value1",
            "field2": "value2",
            "nested": {"field3": "value3"},
        }
        test_dict2 = {
            "field2": "value2",
            "nested": {"field3": "value3"},
            "field1": "value1",
        }
        assert calculate_hash(test_dict1) == calculate_hash(test_dict2)

    def test_calculate_hash_different_data(self):
        """Test que datos distintos producen hashes distintos."""
        hash1 = calculate_hash({"a": 1})
        hash2 = calculate_hash({"a": 2})
        assert hash1 != hash2


class TestHashCalculator:
    """Tests para la clase HashCalculator."""

    def setup_method(self):
        self.calc = HashCalculator()

    def test_calculate_input_hash(self):
        """Test cálculo de hash de input."""
        input_data = {
            "modo": "PERIÓDICA",
            "fecha_ingreso": "2024-01-01",
            "fecha_corte": "2025-01-01",
            "salario_mensual": 2000000,
        }
        result = self.calc.calculate_input_hash(input_data)
        assert result.startswith("sha256:")
        # Debe ser igual al module-level calculate_hash
        assert result == calculate_hash(input_data)

    def test_calculate_output_hash(self):
        """Test cálculo de hash de output."""
        output_data = {
            "meta": {"modo": "PERIÓDICA"},
            "desglose": {"cesantias": {"valor": 1000000}},
        }
        result = self.calc.calculate_output_hash(output_data)
        assert result.startswith("sha256:")
        assert result == calculate_hash(output_data)

    def test_verify_integrity_valid(self):
        """Test verificación de integridad cuando datos coinciden."""
        data = {"key": "value"}
        expected_hash = calculate_hash(data)
        assert self.calc.verify_integrity(data, expected_hash) is True

    def test_verify_integrity_invalid(self):
        """Test verificación de integridad cuando datos NO coinciden."""
        data = {"key": "value"}
        expected_hash = calculate_hash(data)
        data["key"] = "modified"
        assert self.calc.verify_integrity(data, expected_hash) is False
