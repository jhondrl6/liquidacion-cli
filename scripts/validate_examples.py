#!/usr/bin/env python3
"""
Script para validar todos los ejemplos contra resultados esperados
"""
import json
import sys
import argparse
from pathlib import Path
from liquidator.core.engine import LiquidacionEngine
from liquidator.core.input_parser import parse_input_file

def load_expected_results(example_name):
    """Cargar resultados esperados para un ejemplo"""
    expected_path = Path(__file__).parent.parent / "examples" / f"expected_{example_name}.json"
    
    if expected_path.exists():
        with open(expected_path, 'r') as f:
            return json.load(f)
    return None

def validate_example(example_path, engine):
    """Validar un ejemplo individual"""
    print(f"\nValidando ejemplo: {example_path.name}")
    print("-" * 60)
    
    # Parsear input
    input_data = parse_input_file(str(example_path))
    
    # Ejecutar calculo
    resultado = engine.process_input(input_data)
    
    # Guardar resultado actual
    output_path = example_path.parent / f"output_{example_path.stem}.json"
    with open(output_path, 'w') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"+ Resultado guardado en: {output_path}")
    
    # Cargar resultados esperados
    expected = load_expected_results(example_path.stem)
    
    if expected:
        print("Comparando contra resultados esperados...")
        validate_results(resultado, expected)
    else:
        print("! No se encontraron resultados esperados para comparacion")
        print("  Se recomienda generar resultados esperados con --generate-expected")
    
    # Imprimir resumen del compliance
    compliance = resultado["compliance_report"]
    print(f"\nEstado de cumplimiento: {compliance['compliance_status']}")
    print(f"Resumen: {compliance['summary']['passed']} PASADOS, "
          f"{compliance['summary']['warnings']} ADVERTENCIAS, "
          f"{compliance['summary']['failures']} FALLOS")
    
    return compliance['compliance_status'] == "GO"

def validate_results(actual, expected):
    """Validar resultados contra valores esperados"""
    # Validar campos criticos
    campos_criticos = [
        ("total_liquidacion_periodica", "Total liquidacion periodica"),
        ("desglose.cesantias.valor", "Cesantias"),
        ("desglose.intereses_cesantias.valor", "Intereses cesantias"), 
        ("desglose.prima.valor", "Prima"),
        ("compliance_report.compliance_status", "Estado de cumplimiento")
    ]
    
    for campo_path, nombre in campos_criticos:
        try:
            valor_actual = get_nested_value(actual, campo_path)
            valor_esperado = get_nested_value(expected, campo_path)
            
            if isinstance(valor_actual, (int, float)) and isinstance(valor_esperado, (int, float)):
                # Comparacion numerica con margen de tolerancia
                margen = abs(valor_esperado * 0.01)  # 1% de margen
                if abs(valor_actual - valor_esperado) <= margen:
                    print(f"+ {nombre}: {valor_actual:,} (esperado: {valor_esperado:,}) + DENTRO DE MARGEN")
                else:
                    print(f"- {nombre}: {valor_actual:,} (esperado: {valor_esperado:,}) - FUERA DE MARGEN")
            else:
                # Comparacion exacta para otros tipos
                if valor_actual == valor_esperado:
                    print(f"+ {nombre}: {valor_actual} + CORRECTO")
                else:
                    print(f"- {nombre}: {valor_actual} (esperado: {valor_esperado}) - INCORRECTO")
        except (KeyError, TypeError) as e:
            print(f"! {nombre}: No se pudo validar - {str(e)}")

def get_nested_value(obj, path):
    """Obtener valor anidado usando path con puntos"""
    keys = path.split('.')
    for key in keys:
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        else:
            raise KeyError(f"Clave '{key}' no encontrada en path '{path}'")
    return obj

def generate_expected_results(example_path, engine):
    """Generar resultados esperados a partir de un ejemplo"""
    print(f"\nGenerando resultados esperados para: {example_path.name}")
    
    input_data = parse_input_file(str(example_path))
    resultado = engine.process_input(input_data)
    
    # Limpiar campos que cambian (fechas, hashes)
    if "meta" in resultado:
        resultado["meta"]["fecha_generacion"] = "2025-01-01T00:00:00"
        resultado["meta"]["input_hash"] = "sha256:dummy_input_hash"
        resultado["meta"]["output_hash"] = "sha256:dummy_output_hash"
    
    expected_path = Path(__file__).parent.parent / "examples" / f"expected_{example_path.stem}.json"
    with open(expected_path, 'w') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"+ Resultados esperados generados en: {expected_path}")

def main():
    parser = argparse.ArgumentParser(description='Validar ejemplos del sistema de liquidacion')
    parser.add_argument('--all', action='store_true', help='Validar todos los ejemplos')
    parser.add_argument('--example', type=str, help='Validar ejemplo especifico')
    parser.add_argument('--generate-expected', action='store_true', help='Generar resultados esperados')
    parser.add_argument('--verbose', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    engine = LiquidacionEngine()
    examples_dir = Path(__file__).parent.parent / "examples"
    ejemplos_validados = 0
    ejemplos_exitosos = 0
    
    if args.all:
        # Validar todos los ejemplos
        ejemplo_files = list(examples_dir.glob("example_*.json"))
        print(f"\nEncontrados {len(ejemplo_files)} ejemplos para validar")
        
        for ejemplo_file in ejemplo_files:
            if args.generate_expected:
                generate_expected_results(ejemplo_file, engine)
            else:
                exitoso = validate_example(ejemplo_file, engine)
                ejemplos_validados += 1
                if exitoso:
                    ejemplos_exitosos += 1
    
    elif args.example:
        # Validar ejemplo especifico
        ejemplo_file = examples_dir / args.example
        if ejemplo_file.exists():
            if args.generate_expected:
                generate_expected_results(ejemplo_file, engine)
            else:
                exitoso = validate_example(ejemplo_file, engine)
                ejemplos_validados += 1
                if exitoso:
                    ejemplos_exitosos += 1
        else:
            print(f"- Error: Archivo de ejemplo no encontrado: {ejemplo_file}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(0)
    
    # Resumen final
    if ejemplos_validados > 0:
        print("\n" + "="*60)
        print(f"RESUMEN FINAL: {ejemplos_exitosos}/{ejemplos_validados} ejemplos exitosos")
        print("="*60)
        
        if ejemplos_exitosos == ejemplos_validados:
            print("!!! Todos los ejemplos pasaron las validaciones!")
            sys.exit(0)
        else:
            print("- Algunos ejemplos fallaron las validaciones")
            sys.exit(1)

if __name__ == "__main__":
    main()