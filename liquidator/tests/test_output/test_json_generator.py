"""
Tests for JSON Generator
"""

import json
import os
import tempfile
import unittest
from liquidator.output.json_generator import JSONGenerator


class TestJSONGenerator(unittest.TestCase):
    """Test cases for JSONGenerator class"""

    def setUp(self):
        """Set up test fixtures"""
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(current_dir, "..", "output", "schema.json")
        self.generator = JSONGenerator(schema_path)

        # Sample input data
        self.input_data = {
            "modo": "PERIÓDICA",
            "fecha_ingreso": "2024-11-16",
            "fecha_corte": "2025-11-15",
            "salario_mensual": 2000000,
            "reside_en_lugar_trabajo": True,
            "auxilio_conectividad": 200000,
            "comisiones_promedio_mensual": 0,
            "horas_extras_promedio_mensual": 0,
            "dias_vacaciones_pendientes": 0,
            "tipo_contrato": "indefinido",
            "enforce-compliance": True,
            "compliance-policy": "standard",
        }

        # Sample calculation results
        self.calculation_results = {
            "sbl_general": 2200000,
            "sbl_vacaciones": 2000000,
            "cesantias": 2200000,
            "dias_cesantias": 360,
            "plazo_cesantias": "2026-02-14",
            "intereses_cesantias": 264000,
            "dias_intereses": 360,
            "plazo_intereses": "2026-01-31",
            "prima": 1100000,
            "dias_prima": 180,
            "plazo_prima": "2025-12-31",
            "vacaciones": 0,
            "dias_vacaciones": 0,
            "validaciones_y_alertas": {
                "auxilio_transporte_excluido": "Residencia en el lugar de trabajo (Finca).",
                "auxilio_conectividad_advertencia": "Verificar si está pactado como parte del salario habitual.",
            },
        }

        # Sample compliance report
        self.compliance_report = {
            "compliance_status": "GO",
            "summary": {"passed": 25, "warnings": 3, "failures": 0},
            "checks": [
                {
                    "id": "V001",
                    "description": "Parametros oficiales 2025 presentes y consistentes",
                    "result": "PASS",
                    "evidence": "SMMLV=1423500 matches params/2025.json",
                    "rule_ref": ["Decreto 1572/2024"],
                }
            ],
            "blocking_failures": [],
            "params_version": "2025-10-31",
            "timestamp": "2025-11-02T07:25:00-05:00",
            "input_hash": "sha256:abcd...",
            "output_hash": "sha256:ef01...",
            "operator_action": {
                "action": "auto",
                "operator_id": None,
                "justification": None,
            },
        }

        # Sample params
        self.params = {
            "version": "2025-10-31",
            "SMMLV": 1423500,
            "AUXILIO_TRANS": 200000,
            "LIMITE_AUXILIO": 2847000,
            "TASA_INT_CESANTIAS": 0.12,
            "DIAS_BASE": 360,
            "TOPE_INDEMNIZACION_SMMLV": 20,
            "FECHA_APLICACION_RECARGO_DOMINICAL": "2025-07-01",
        }

    def test_generate_json(self):
        """Test JSON generation"""
        output = self.generator.generate_json(
            self.input_data,
            self.calculation_results,
            self.compliance_report,
            self.params,
        )

        # Check structure
        self.assertIn("meta", output)
        self.assertIn("trabajador", output)
        self.assertIn("parametros", output)
        self.assertIn("desglose", output)
        self.assertIn("total_liquidacion_periodica", output)
        self.assertIn("validaciones_y_alertas", output)
        self.assertIn("normas_aplicadas", output)
        self.assertIn("compliance_report", output)

        # Check meta section
        self.assertEqual(output["meta"]["modo"], "PERIÓDICA")
        self.assertEqual(output["meta"]["fecha_ingreso"], "2024-11-16")
        self.assertEqual(output["meta"]["fecha_corte"], "2025-11-15")
        self.assertEqual(output["meta"]["params_version"], "2025-10-31")
        self.assertTrue(output["meta"]["input_hash"].startswith("sha256:"))
        self.assertTrue(output["meta"]["output_hash"].startswith("sha256:"))

        # Check worker section
        self.assertEqual(output["trabajador"]["tipo_contrato"], "indefinido")
        self.assertTrue(output["trabajador"]["reside_en_lugar_trabajo"])

        # Check parameters section
        self.assertEqual(output["parametros"]["SMMLV"], 1423500)
        self.assertEqual(output["parametros"]["AUXILIO_TRANS"], 200000)

        # Check breakdown section
        self.assertEqual(output["desglose"]["SBL_GENERAL"], 2200000)
        self.assertEqual(output["desglose"]["cesantias"]["valor"], 2200000)
        self.assertEqual(output["desglose"]["cesantias"]["dias_liquidados"], 360)
        self.assertEqual(
            output["desglose"]["cesantias"]["plazo_pago_legal"], "2026-02-14"
        )

        # Check total
        self.assertEqual(output["total_liquidacion_periodica"], 3564000)

        # Check compliance report
        self.assertEqual(output["compliance_report"]["compliance_status"], "GO")
        self.assertEqual(output["compliance_report"]["summary"]["passed"], 25)

    def test_generate_json_finiquito(self):
        """Test JSON generation for FINIQUITO mode"""
        # Update input to FINIQUITO mode
        self.input_data["modo"] = "FINIQUITO"

        # Add finiquito-specific calculation results
        self.calculation_results["indemnizacion"] = 4400000
        self.calculation_results["dias_servicio"] = 360
        self.calculation_results["salario_pendiente"] = 0

        output = self.generator.generate_json(
            self.input_data,
            self.calculation_results,
            self.compliance_report,
            self.params,
        )

        # Check that total_liquidacion_finiquito is present
        self.assertIn("total_liquidacion_finiquito", output)
        self.assertNotIn("total_liquidacion_periodica", output)

        # Check that indemnization and salary pending are present
        self.assertIn("indemnizacion", output["desglose"])
        self.assertIn("salario_pendiente", output["desglose"])

    def test_save_json(self):
        """Test saving JSON to file"""
        output = self.generator.generate_json(
            self.input_data,
            self.calculation_results,
            self.compliance_report,
            self.params,
        )

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_path = f.name

        try:
            # Save JSON
            result = self.generator.save_json(output, temp_path)
            self.assertTrue(result)

            # Verify file exists and contains valid JSON
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path, "r") as f:
                loaded_data = json.load(f)

            # Verify content
            self.assertEqual(loaded_data["meta"]["modo"], "PERIÓDICA")
            self.assertEqual(loaded_data["total_liquidacion_periodica"], 3564000)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_hash_calculation(self):
        """Test hash calculation"""
        data1 = {"a": 1, "b": 2}
        data2 = {"b": 2, "a": 1}  # Same content, different order
        data3 = {"a": 1, "b": 3}  # Different content

        hash1 = self.generator._calculate_hash(data1)
        hash2 = self.generator._calculate_hash(data2)
        hash3 = self.generator._calculate_hash(data3)

        # Same content should produce same hash regardless of key order
        self.assertEqual(hash1, hash2)
        # Different content should produce different hash
        self.assertNotEqual(hash1, hash3)


if __name__ == "__main__":
    unittest.main()
