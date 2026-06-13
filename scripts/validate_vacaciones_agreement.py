
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from liquidator.core.engine import LiquidacionEngine
from liquidator.output.pdf_generator import PDFGenerator

def test_vacaciones_agreement():
    print("=== Iniciando Prueba de Compensación de Vacaciones ===")
    
    # 1. Configurar datos de prueba
    input_data = {
        "modo": "PERIODICA",
        "fecha_ingreso": "2024-01-01",
        "fecha_corte": "2024-12-30", # ~1 año
        "salario_mensual": 2000000,
        "dias_vacaciones_pendientes": 15,
        "dias_vacaciones_para_compensar_dinero": 7, # Valido (<= 7.5)
        "nombre": "Test Worker",
        "documento": "12345",
        "tipo_contrato": "indefinido"
    }
    
    # 2. Ejecutar motor
    engine = LiquidacionEngine()
    result = engine.process(input_data)
    
    # 3. Validar JSON
    print("\n--- Validando JSON ---")
    vacaciones = result.get("desglose", {}).get("vacaciones", {})
    if vacaciones and vacaciones.get("valor", 0) > 0:
        print(f"[PASS] Valor vacaciones calculado: {vacaciones['valor']}")
        print(f"       Días liquidados: {vacaciones.get('dias_liquidados')}")
        print(f"       Nota: {vacaciones.get('nota')}")
    else:
        print("[FAIL] No se calcularon vacaciones compensadas")
        print(json.dumps(result.get("desglose"), indent=2))
        return

    # 4. Validar Generación de Documento
    print("\n--- Validando Documento (PDF/TXT) ---")
    generator = PDFGenerator()
    # Force txt fallback for checking content easily if dependencies are missing
    # But we want to test the template rendering logic which happens in _render_markdown_template
    
    # We can call _render_markdown_template directly to check content
    try:
        context = generator._build_template_context(result)
        rendered = generator._render_markdown_template("periodica", context)
        
        print("Buscando cláusula en el template renderizado...")
        clause_text = "CLÁUSULA DE ACUERDO DE COMPENSACIÓN DE VACACIONES"
        article_ref = "Artículo 189"
        
        if clause_text in rendered:
            print(f"[PASS] Cláusula encontrada: '{clause_text}'")
        else:
            print(f"[FAIL] Cláusula NO encontrada en el documento")
            print("Contenido parcial:")
            print(rendered[:500])
            
        if article_ref in rendered:
            print(f"[PASS] Referencia legal encontrada: '{article_ref}'")
        else:
            print(f"[FAIL] Referencia legal {article_ref} NO encontrada")

    except Exception as e:
        print(f"[ERROR] Falló la renderización del template: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vacaciones_agreement()
