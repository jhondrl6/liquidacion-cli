# Liquidación CLI v2.0 — Liquidación de Nómina Colombia

Herramienta CLI local para el cálculo de prestaciones sociales en Colombia conforme a la normativa laboral vigente (2025-2026). Calcula liquidaciones periódicas y de finiquito con cumplimiento legal automático, motor de compliance, y segundo cerebro local versionado.

## Características Principales

- ✅ **Cálculos Legales Precisos**: Implementa fórmulas oficiales del CST y leyes vigentes
- ✅ **Cumplimiento Automático**: Sistema con 10 validaciones legales predefinidas (V001-V010)
- ✅ **Múltiples Modos**: Soporta liquidaciones PERIÓDICAS y de FINIQUITO
- ✅ **Compensación Vacaciones**: Soporte para pago en dinero por acuerdo mutuo (Art. 189 CST)
- ✅ **Salidas Profesionales**: JSON estructurado, Markdown legible y PDF exportable
- ✅ **Auditoría Completa**: Trazabilidad con hash, timestamps y versionamiento
- ✅ **Casos Especiales**: Manejo de trabajadores de finca rural, salarios variables y más

## Instalación Rápida

### Requisitos
- Python 3.11+

### Instalación desde repositorio
```bash
git clone https://github.com/jhondrl6/liquidacion-cli.git
cd liquidacion-cli
pip install -e .
# O con uv:
uv pip install -e .
```
El entry point `liquidacion` queda disponible en el PATH.

## Uso Básico

```bash
# Ver ayuda
liquidacion --help
liquidacion liquidar --help

# Caso canónico (206 días, 2 segmentos, SBL $2.200.000)
liquidacion liquidar examples/inputs/caso_canonico_periodico_206d.json

# Validar un input contra parámetros 2025
liquidacion validate examples/inputs/test_minimo_valid.json --params-year 2025

# Ver información del sistema
liquidacion info
```

## Ejemplos Disponibles

El directorio `examples/` contiene casos de prueba documentados:

- `example_finca_rural.json` - Trabajador que reside en finca (sin auxilio transporte)
- `example_salario_variable.json` - Salarios variables con promediación
- `example_finiquito.json` - Liquidación completa con indemnización
- `example_periodo_parcial.json` - Ingreso a mitad de semestre

Consulte `examples/README_examples.md` para详细了解 cada caso.

## Estructura de Entrada (JSON)

```json
{
  "modo": "PERIODICA",
  "fecha_ingreso": "2024-11-16",
  "fecha_corte": "2025-11-15",
  "salario_mensual": 2000000,
  "reside_en_lugar_trabajo": true,
  "auxilio_conectividad": 200000,
  "comisiones_promedio_mensual": 0,
  "horas_extras_promedio_mensual": 0,
  "bonificaciones_promedio_mensual": 0,
  "dias_vacaciones_pendientes": 0,
  "dias_vacaciones_para_compensar_dinero": 0,
  "tipo_contrato": "indefinido",
  "enforce-compliance": true,
  "compliance-policy": "standard"
}
```

## Estructura de Salida

El sistema genera un JSON completo con:

```json
{
  "meta": {
    "modo": "PERIÓDICA",
    "fecha_generacion": "2025-11-04T10:00:00",
    "params_version": "2025-10-31"
  },
  "parametros": {
    "SMMLV": 1423500,
    "AUXILIO_TRANS": 200000,
    "LIMITE_AUXILIO": 2847000,
    "TASA_INT_CESANTIAS": 0.12
  },
  "desglose": {
    "SBL_GENERAL": 2200000,
    "cesantias": {
      "valor": 2200000,
      "dias_liquidados": 365,
      "plazo_pago_legal": "2026-02-14",
      "norma": "Art.249-250 CST"
    },
    "intereses_cesantias": {
      "valor": 264000,
      "dias_liquidados": 365,
      "plazo_pago_legal": "2026-01-31",
      "norma": "Ley 50/1990 Art.99"
    },
    "prima": {
      "valor": 1100000,
      "dias_liquidados": 180,
      "plazo_pago_legal": "2025-12-31",
      "norma": "Art.306-308 CST"
    }
  },
  "compliance_report": {
    "compliance_status": "GO",
    "summary": {
      "passed": 10,
      "warnings": 0,
      "failures": 0
    }
  }
}
```

## Cumplimiento Legal

El sistema implementa 10 validaciones automáticas:

| ID | Descripción | Referencia Legal |
|----|-------------|------------------|
| V001 | Parámetros oficiales 2025 | Decreto 1572/2024 |
| V002 | Contrato válido | Art. 23 CST |
| V003 | Auxilio transporte aplicado correctamente | CHECKLIST Auxilio Transporte |
| V004 | Fórmulas de cesantías correctas | Art. 249-250 CST |
| V005 | Intereses tasa 12% | Ley 50/1990 Art.99 |
| V006 | Prima semestre proporcional | Art.306-308 CST |
| V007 | Vacaciones excluidas en periódica | Arts.186-192 CST |
| V008 | Plazos de pago documentados | Art.65 CST |
| V009 | Sustento legal presente | CHECKLIST Normas |
| V010 | Hashes y versionamiento | CHECKLIST Trazabilidad |

## Testing

Para ejecutar la suite completa de pruebas:

```bash
# Ejecutar todos los tests
uv run --with pytest --with python-dateutil --with PyYAML \
  --with jsonschema --with pydantic --with loguru --with click \
  --with markdown --with Jinja2 pytest liquidator/tests -q
```

## Documentación

La documentación completa está disponible en:

- [Plan de Implementación](docs/Plan de Implementación.md) - Arquitectura detallada y diseño
- [Documentación Técnica Completa](docs/SESION_15_DOCUMENTACION_TECNICA_COMPLETA.md) - Especificación exhaustiva
- [Ejemplos y Casos de Prueba](examples/README_examples.md) - Casos de uso documentados
- [Referencias Legales](legal_docs/) - Normativa completa y plazos

## Configuración

El sistema se configura mediante archivos en `config/`:

- `default_config.yaml` - Configuración principal del sistema
- `compliance_policies.yaml` - Políticas de cumplimiento (lenient/standard/strict)
- `logging_config.yaml` - Configuración de logs

## Licencia

MIT License - Ver archivo LICENSE para detalles.

## Soporte

Para soporte o preguntas:

1. Revisar [documentación de troubleshooting](docs/troubleshooting.md)
2. Consultar [ejemplos disponibles](examples/README_examples.md)
3. Verificar [logs de auditoría](audit/logs/) para diagnóstico

---

**Versión**: 2.0.0  
**Última Actualización**: 2026-06-14  
**Compatibilidad**: Ley Laboral Colombia 2025-2026
