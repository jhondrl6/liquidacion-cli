import json
import os
import shutil
import tempfile
import unittest
from liquidator.params.params_loader import ParamsLoader, ParamsError


class TestParamsLoader(unittest.TestCase):
    """Test cases for ParamsLoader class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for params
        self.temp_dir = tempfile.mkdtemp()

        # Copy schema to temp directory
        current_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        schema_path = os.path.join(current_dir, "params", "schema.json")
        temp_schema_path = os.path.join(self.temp_dir, "schema.json")
        if os.path.exists(schema_path):
            shutil.copy(schema_path, temp_schema_path)

        self.loader = ParamsLoader(self.temp_dir)

        # Create test params file
        self.test_params = {
            "version": "2025-10-31",
            "SMMLV": 1423500,
            "AUXILIO_TRANS": 200000,
            "LIMITE_AUXILIO": 2847000,
            "TASA_INT_CESANTIAS": 0.12,
            "DIAS_BASE": 360,
            "TOPE_INDEMNIZACION_SMMLV": 20,
            "FECHA_APLICACION_RECARGO_DOMINICAL": "2025-07-01",
        }

        # Save test params file
        self.params_path = os.path.join(self.temp_dir, "2025.json")
        with open(self.params_path, "w") as f:
            json.dump(self.test_params, f)

    def tearDown(self):
        """Clean up after tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default(self):
        """Test initialization with default params directory"""
        loader = ParamsLoader()
        self.assertEqual(loader.params_dir, "params")
        self.assertIsNotNone(loader.schema_path)
        self.assertTrue(loader.schema_path.endswith("schema.json"))

    def test_init_custom_dir(self):
        """Test initialization with custom params directory"""
        custom_dir = "/tmp/custom_params"
        loader = ParamsLoader(custom_dir)
        self.assertEqual(loader.params_dir, custom_dir)
        self.assertEqual(loader.schema_path, os.path.join(custom_dir, "schema.json"))

    def test_load_success(self):
        """Test successful parameter loading"""
        params = self.loader.load(2025)
        self.assertEqual(params["SMMLV"], 1423500)
        self.assertEqual(params["version"], "2025-10-31")

    def test_load_with_validation(self):
        """Test parameter loading with validation enabled"""
        params = self.loader.load(2025, validate=True)
        self.assertEqual(params["SMMLV"], 1423500)
        self.assertEqual(params["version"], "2025-10-31")

    def test_load_no_validation(self):
        """Test parameter loading with validation disabled"""
        params = self.loader.load(2025, validate=False)
        self.assertEqual(params["SMMLV"], 1423500)
        self.assertEqual(params["version"], "2025-10-31")

    def test_load_explicit_path(self):
        """Test loading with explicit file path"""
        custom_path = os.path.join(self.temp_dir, "custom.json")
        with open(custom_path, "w") as f:
            json.dump(self.test_params, f)

        params = self.loader.load(2025, path=custom_path)
        self.assertEqual(params["SMMLV"], 1423500)

    def test_load_file_not_found(self):
        """Test error when params file doesn't exist"""
        with self.assertRaises(ParamsError) as cm:
            self.loader.load(2024)  # Year that doesn't have a file
        self.assertIn("No se encontró el archivo", str(cm.exception))

    def test_load_invalid_json(self):
        """Test error when params file has invalid JSON"""
        invalid_path = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_path, "w") as f:
            f.write("{ invalid json")

        with self.assertRaises(ParamsError) as cm:
            self.loader.load(2023, path=invalid_path)
        self.assertIn("JSON inválido", str(cm.exception))

    def test_load_schema_missing(self):
        """Test loading when schema file is missing"""
        # Remove schema file
        schema_path = os.path.join(self.temp_dir, "schema.json")
        if os.path.exists(schema_path):
            os.remove(schema_path)

        # Create new loader after removing schema
        loader = ParamsLoader(self.temp_dir)

        # Should still work without validation
        params = loader.load(2025, validate=False)
        self.assertEqual(params["SMMLV"], 1423500)

        # Validation should fail gracefully
        params = loader.load(2025, validate=True)
        self.assertEqual(params["SMMLV"], 1423500)

    def test_load_unicode_content(self):
        """Test loading params with unicode content"""
        unicode_params = {
            "versión": "2025-10-31",
            "descripción": "Parámetros con caracteres especiales",
            "SMMLV": 1423500,
        }
        unicode_path = os.path.join(self.temp_dir, "unicode.json")
        with open(unicode_path, "w", encoding="utf-8") as f:
            json.dump(unicode_params, f, ensure_ascii=False)

        params = self.loader.load(2025, path=unicode_path)
        self.assertEqual(params["descripción"], "Parámetros con caracteres especiales")
        self.assertEqual(params["versión"], "2025-10-31")


if __name__ == "__main__":
    unittest.main()
