"""
Tests para el módulo de hash calculator.
"""

import pytest
from liquidator.audit.hash_calculator import HashCalculator


class TestHashCalculator:
    """Tests para HashCalculator."""

    def setup_method(self):
        """Configuración antes de cada test."""
        self.hash_calculator = HashCalculator()

    def test_calculate_hash_string(self):
        """Test cálculo de hash para string."""
        test_string = "test_string_123"
        hash_result = self.hash_calculator.calculate_hash(test_string)

        assert hash_result.startswith("sha256:")
        assert len(hash_result) == 71  # sha256: + 64 caracteres hex

    def test_calculate_hash_dict_deterministic(self):
        """Test que el hash de dict es determinístico."""
        test_dict = {
            "field1": "value1",
            "field2": "value2",
            "nested": {"field3": "value3"},
        }

        # Mismo dict, diferente orden
        test_dict2 = {
            "field2": "value2",
            "nested": {"field3": "value3"},
            "field1": "value1",
        }

        hash1 = self.hash_calculator.calculate_hash(test_dict)
        hash2 = self.hash_calculator.calculate_hash(test_dict2)

        assert hash1 == hash2

    def test_calculate_input_hash(self):
        """Test cálculo de hash de input."""
        input_data = {
            "modo": "PERIÓDICA",
            "fecha_ingreso": "2024-01-01",
            "fecha_corte": "2025-01-01",
            "salario_mensual": 2000000,
            "human_override": True,
            "operator_id": "OP001",
        }

        input_hash = self.hash_calculator.calculate_input_hash(input_data)

        assert input_hash.startswith("sha256:")
        # El hash no debe incluir campos de override
        input_without_override = input_data.copy()
        input_without_override.pop("human_override")
        input_without_override.pop("operator_id")

        expected_hash = self.hash_calculator.calculate_hash(input_without_override)
        assert input_hash == expected_hash

    def test_calculate_output_hash(self):
        """Test cálculo de hash de output."""
        output_data = {
            "meta": {
                "fecha_generacion": "2025-01-01T10:00:00",
                "output_hash": "sha256:previous_hash",
            },
            "desglose": {"cesantias": {"valor": 1000000}},
            "compliance_report": {"timestamp": "2025-01-01T10:00:00"},
        }

        output_hash = self.hash_calculator.calculate_output_hash(output_data)

        # El hash debe ser consistente excluyendo campos variables
        output_consistent = output_data.copy()
        output_consistent["meta"].pop("fecha_generacion")
        output_consistent["meta"].pop("output_hash")
        output_consistent["compliance_report"].pop("timestamp")

        expected_hash = self.hash_calculator.calculate_hash(output_consistent)
        assert output_hash == expected_hash

    def test_verify_output_integrity(self):
        """Test verificación de integridad de output."""
        output_data = {
            "desglose": {"cesantias": {"valor": 1000000}},
            "meta": {"fecha_generacion": "2025-01-01T10:00:00"},
        }

        # Calcular hash esperado
        expected_hash = self.hash_calculator.calculate_output_hash(output_data)

        # Verificar integridad
        is_valid = self.hash_calculator.verify_output_integrity(
            output_data, expected_hash
        )
        assert is_valid is True

        # Modificar datos y verificar que falla
        output_data["desglose"]["cesantias"]["valor"] = 2000000
        is_valid = self.hash_calculator.verify_output_integrity(
            output_data, expected_hash
        )
        assert is_valid is False

    def test_generate_hash_report(self):
        """Test generación de reporte de hashes."""
        input_hash = "sha256:input123"
        output_hash = "sha256:output456"
        params_version = "2025-01-01"

        report = self.hash_calculator.generate_hash_report(
            input_hash, output_hash, params_version
        )

        assert report["input_hash"] == input_hash
        assert report["output_hash"] == output_hash
        assert report["params_version"] == params_version
        assert report["hash_algorithm"] == "sha256"
        assert report["verification_status"] == "HASHES_CALCULATED"
