#!/usr/bin/env python3
"""
Entry-point CLI para liquidacion - compatible ASCII.
"""
import argparse
import json
import sys
from pathlib import Path

from liquidator.core.engine import LiquidacionEngine
from liquidator.output.pdf_generator import (
    generate_liquidacion_pdf,
    generate_pdf_from_json,
)
from liquidator.utils.error_handler import LiquidacionError


def build_parser():
    """Construye parser con flags de la SESION 13."""
    p = argparse.ArgumentParser(prog='liquidar',
                                description='Liquidacion de nomina Colombia 2025')
    p.add_argument('--input', '-i',
                   help='Archivo JSON de entrada (sobrescribe flags)')
    p.add_argument('--output', '-o',
                   help='Ruta del JSON de salida')

    p.add_argument('--modo', choices=['PERIODICA', 'FINIQUITO'],
                   help='Modo de liquidacion')
    p.add_argument('--fecha_ingreso',
                   help='Fecha de ingreso YYYY-MM-DD')
    p.add_argument('--fecha_corte',
                   help='Fecha de corte YYYY-MM-DD')
    p.add_argument('--salario_mensual', type=int,
                   help='Salario base mensual COP')
    p.add_argument('--reside_en_lugar_trabajo',
                   type=lambda x: (x.lower() if x is not None else '').strip() == 'true',
                   help='true/false: reside en lugar de trabajo')
    p.add_argument('--auxilio_transporte', type=int, default=0,
                   help='Valor auxilio de transporte COP')
    p.add_argument('--nombre-trabajador', 
                   help='Nombre completo del trabajador')
    p.add_argument('--documento-trabajador', 
                   help='Número de documento del trabajador')
    p.add_argument('--tipo_contrato',
                   choices=['indefinido', 'fijo'],
                   help='Tipo de contrato')

    # Compliance
    p.add_argument('--enforce-compliance',
                   type=lambda x: (x.lower() if x is not None else '').strip() == 'true',
                   default=True,
                   help='Forzar cumplimiento legal')
    p.add_argument('--compliance-policy',
                   choices=['lenient', 'standard', 'strict'],
                   default='standard',
                   help='Politica de cumplimiento')
    p.add_argument('--human-override', action='store_true',
                   help='Permitir bypass con justificacion')
    p.add_argument('--operator-id',
                   help='Identificador del operador que autoriza')
    p.add_argument('--override-reason',
                   help='Justificacion del override')

    # Modos especiales
    p.add_argument('--test-run', action='store_true',
                   help='Ejecutar suite de validacion interna')
    p.add_argument('--generate-pdf', metavar='JSON_PATH|AUTO',
                   help='Generar PDF a partir de JSON existente o AUTO para usar el resultado actual')
    p.add_argument('--compliance-check-only', metavar='JSON_PATH',
                   help='Solo ejecutar validaciones de compliance')
    return p


def main(argv=None):
    """Funcion main expuesta para CLI y tests."""
    parser = build_parser()
    args = parser.parse_args(argv)
    
    

    try:
        if args.test_run:
            from liquidator.tests.runner import run_suite
            return run_suite()

        if args.generate_pdf and args.generate_pdf.lower() != 'auto':
            pdf_path = generate_pdf_from_json(args.generate_pdf)
            print('PDF generado: {}'.format(pdf_path))
            return 0

        if args.compliance_check_only:
                data = json.load(open(args.compliance_check_only,
                                      encoding='utf-8'))
                report = LiquidacionEngine().compliance_check(data)
                print(json.dumps(report, indent=2))
                return 0 if report['compliance_status'] == 'GO' else 1

        # Flujo normal
        if args.input:
            data = json.load(open(args.input, encoding='utf-8'))
        else:
            data = {k: v for k, v in vars(args).items() if v is not None}

        # Crear o actualizar sección del trabajador con datos de CLI si existen
        try:
            if hasattr(args, 'nombre_trabajador') and args.nombre_trabajador is not None and str(args.nombre_trabajador).strip():
                if 'trabajador' not in data:
                    data['trabajador'] = {}
                data['trabajador']['nombre'] = str(args.nombre_trabajador).strip()
                data['nombre'] = str(args.nombre_trabajador).strip()  # Para compatibilidad
                
            if hasattr(args, 'documento_trabajador') and args.documento_trabajador is not None and str(args.documento_trabajador).strip():
                if 'trabajador' not in data:
                    data['trabajador'] = {}
                data['trabajador']['documento'] = str(args.documento_trabajador).strip()
                data['documento'] = str(args.documento_trabajador).strip()  # Para compatibilidad
        except Exception as e:
            print(f"Error procesando datos del trabajador: {e}")
            # Continuar con los datos que puedan funcionar
            
        # Mantener lógica existente para datos existentes
        trabajador_info = data.get('trabajador')
        if isinstance(trabajador_info, dict):
            if 'nombre' not in data:
                data.setdefault('nombre', trabajador_info.get('nombre'))
            if 'documento' not in data:
                data.setdefault('documento', trabajador_info.get('documento'))
            data.setdefault('tipo_contrato', trabajador_info.get('tipo_contrato') or 'indefinido')
            if 'reside_en_lugar_trabajo' in trabajador_info:
                data.setdefault('reside_en_lugar_trabajo', trabajador_info.get('reside_en_lugar_trabajo'))
                
        # Asegurar que tipo_contrato siempre tenga un valor
        if 'tipo_contrato' not in data or data.get('tipo_contrato') is None:
            data['tipo_contrato'] = 'indefinido'

        empleador_info = data.get('empresa') or data.get('empleador')
        if isinstance(empleador_info, dict):
            data.setdefault('empresa', empleador_info)

        result = LiquidacionEngine().process(data)

        out_path = args.output or 'liquidacion_out.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        print('[OK] Liquidacion finalizada')
        print('    JSON generado: {}'.format(out_path))

        if args.generate_pdf and args.generate_pdf.lower() == 'auto':
            pdf_output = Path(out_path).with_suffix('.pdf')
            generated_pdf = generate_liquidacion_pdf(result, output_path=pdf_output)
            print('    PDF generado:  {}'.format(generated_pdf))
        return 0

    except LiquidacionError as e:
        print('Error: {}'.format(e), file=sys.stderr)
        return 1
    except Exception as e:
        print('Error inesperado: {}'.format(e), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())