#!/usr/bin/env python3
"""
Script para generar liquidaciones de múltiples trabajadores
"""

import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from liquidator.core.engine import LiquidacionEngine
from liquidator.output.pdf_generator import generate_liquidacion_pdf

# Lista de trabajadores con sus datos
trabajadores = [
    {
        "nombre": "MARÍA GONZÁLEZ PÉREZ",
        "documento": "52.123.876",
        "salario_mensual": 1500000,
        "reside_en_lugar_trabajo": True
    },
    {
        "nombre": "JUAN CARLOS RODRÍGUEZ", 
        "documento": "78.456.231",
        "salario_mensual": 1800000,
        "reside_en_lugar_trabajo": False
    },
    {
        "nombre": "ANA LUCÍA MORALES",
        "documento": "91.789.345", 
        "salario_mensual": 2000000,
        "reside_en_lugar_trabajo": False
    }
]

def generar_liquidacion_trabajador(trabajador_data):
    """Genera liquidación para un trabajador específico"""
    
    # Preparar datos de liquidación
    data = {
        "modo": "PERIODICA",
        "fecha_ingreso": "2024-11-16",
        "fecha_corte": "2025-11-15",
        "salario_mensual": trabajador_data["salario_mensual"],
        "reside_en_lugar_trabajo": trabajador_data["reside_en_lugar_trabajo"],
        "auxilio_transporte": 200000,
        "trabajador": {
            "nombre": trabajador_data["nombre"],
            "documento": trabajador_data["documento"]
        }
    }
    
    # Procesar liquidación
    engine = LiquidacionEngine()
    result = engine.process(data)
    
    # Generar nombres de archivo
    nombre_archivo = trabajador_data["nombre"].lower().replace(" ", "_").replace(".", "")
    output_file = Path(f"liquidacion_{nombre_archivo}.json")
    
    # Guardar JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f'Liquidación generada para: {trabajador_data["nombre"]}')
    print(f'Archivo JSON: {output_file}')
    
    # Generar PDF
    try:
        pdf_path = output_file.with_suffix('.pdf')
        generated_pdf = generate_liquidacion_pdf(result, output_path=pdf_path)
        print(f'Archivo PDF: {generated_pdf}')
    except Exception as e:
        print(f'Error generando PDF: {e}')
    
    print("-" * 50)
    return result

def main():
    # Generar liquidaciones para todos los trabajadores
    for trabajador in trabajadores:
        generar_liquidacion_trabajador(trabajador)
    
    print(f"\nTotal de liquidaciones generadas: {len(trabajadores)}")

if __name__ == '__main__':
    main()
