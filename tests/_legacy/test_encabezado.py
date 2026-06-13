#!/usr/bin/env python3
import sys
sys.path.insert(0, sys.path[0] + '/../..')

from liquidator.output.pdf_generator import PDFGenerator

def test_encabezado():
    # Datos de prueba con y sin datos de empresa
    test_cases = [
        {
            "nombre": "Sin empresa - debe usar defaults",
            "empresa": {}
        },
        {
            "nombre": "Con datos empresa personalizados",
            "empresa": {
                "nombre": "MI EMPRESA PERSONALIZADA SAS",
                "nit": "NIT 123.456.789-0"
            }
        }
    ]
    
    generator = PDFGenerator()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"=== Test Case {i}: {test_case['nombre']} ===")
        header_content = generator._generate_header_content(test_case)
        print("Header HTML Generado:")
        print(header_content)
        print("\n" + "="*50 + "\n")
    
    # También verificar si la plantilla markdown se está usando correctamente
    print("\n=== Verificación de Plantilla Markdown ===")
    template_content = generator._load_markdown_template("comprobante_periodica.md")
    print("Contenido de plantilla (búsqueda de Empresa Liquidaciones SAS):")
    
    if "Empresa Liquidaciones SAS" in template_content:
        print("ERROR: Plantilla contiene 'Empresa Liquidaciones SAS' - debe corregirse")
    elif "Hildaliria Raigoza L." in template_content and "CC 42.066.783" in template_content:
        print("OK: Plantilla ya tiene valores correctos")
    else:
        print("ADVERTENCIA: Plantilla en estado desconocido")

if __name__ == '__main__':
    test_encabezado()
