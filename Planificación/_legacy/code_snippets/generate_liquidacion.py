# DEPRECATED: usar python -m liquidator.cli
# Movido a scripts/_legacy/ en Fase 0 — Tarea 0.C (2026-06-12)

#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from liquidator.core.engine import LiquidacionEngine
from liquidator.output.pdf_generator import generate_liquidacion_pdf

def main():
    # Load the updated example
    project_root = Path(__file__).parent
    with open(project_root / 'examples' / 'example_finca_rural.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Si usa el antiguo campo, migrarlo al nuevo
    if 'auxilio_conectividad' in data:
        data['auxilio_transporte'] = data.pop('auxilio_conectividad')
    
    # Process the liquidation
    engine = LiquidacionEngine()
    result = engine.process(data)
    
    # Save JSON output
    project_root = Path(__file__).parent
    output_file = project_root / 'liquidacion_pedro_franco.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f'[OK] Liquidación finalizada')
    print(f'    JSON generado: {output_file}')
    
    # Generate PDF
    try:
        pdf_output = output_file.with_suffix('.pdf')
        generated_pdf = generate_liquidacion_pdf(result, output_path=pdf_output)
        print(f'    PDF generado:  {generated_pdf}')
    except Exception as e:
        print(f'    Error generando PDF: {e}')
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
