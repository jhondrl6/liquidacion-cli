import json
from datetime import datetime
from typing import Dict, Any
from hashlib import sha256


def write_json_file(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class JSONGenerator:
    def __init__(self):
        pass

    def generate_output(
        self,
        input_data: Dict[str, Any],
        calculation_result: Dict[str, Any],
        compliance_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output with all required fields
        """
        # Calculate hashes
        input_hash = self._calculate_hash(input_data)

        # Create output structure
        output = {
            "meta": {
                "modo": input_data.get("modo", "PERIODICA"),
                "fecha_generacion": datetime.now().isoformat(),
                "fecha_corte": input_data.get("fecha_corte"),
                "fecha_ingreso": input_data.get("fecha_ingreso"),
                "moneda": "COP",
                "params_version": "2025-10-31",
                "input_hash": input_hash,
                "output_hash": None,  # Will be calculated after the full output is created
                "generator_version": "1.0.0",
            },
            "trabajador": {
                "nombre": input_data.get("trabajador", {}).get("nombre", input_data.get("nombre", "")),
                "documento": input_data.get("trabajador", {}).get("documento", input_data.get("documento", "")),
                "tipo_contrato": input_data.get("trabajador", {}).get("tipo_contrato", input_data.get("tipo_contrato", "indefinido")),
                "reside_en_lugar_trabajo": input_data.get("trabajador", {}).get("reside_en_lugar_trabajo", input_data.get(
                    "reside_en_lugar_trabajo", False
                )),
            },
            "parametros": {
                "SMMLV": 1423500,
                "AUXILIO_TRANS": 200000,
                "LIMITE_AUXILIO": 2847000,
                "TASA_INT_CESANTIAS": 0.12,
                "DIAS_BASE": 360,
                "TOPE_INDEMNIZACION_SMMLV": 20,
                "FECHA_APLICACION_RECARGO_DOMINICAL": "2025-07-01",
            },
            "desglose": calculation_result.get("desglose", {}),
            "total_liquidacion": calculation_result.get("total", 0),
            "validaciones_y_alertas": calculation_result.get("alertas", {}),
            "normas_aplicadas": calculation_result.get("normas", []),
            "compliance_report": compliance_result,
        }

        # Calculate output hash
        output["meta"]["output_hash"] = self._calculate_hash(output)

        return output

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """
        Calculate SHA-256 hash of data structure
        """
        # Convert data to json string for consistent hashing
        json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return f"sha256:{sha256(json_str.encode('utf-8')).hexdigest()}"

    def generate_json(
        self,
        input_data: Dict[str, Any],
        calculation_result: Dict[str, Any],
        compliance_result: Dict[str, Any],
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output - alias for generate_output to maintain compatibility
        """
        return self.generate_output(input_data, calculation_result, compliance_result)

    def save_to_file(self, output: Dict[str, Any], filepath: str) -> None:
        """
        Save JSON output to file
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False, sort_keys=True)
