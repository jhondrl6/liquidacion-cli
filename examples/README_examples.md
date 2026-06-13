# Ejemplos de Casos de Uso - Sistema de Liquidación de Nómina Colombia 2025

Este directorio contiene ejemplos completos que demuestran diferentes escenarios de uso del sistema. Cada ejemplo está diseñado para validar funcionalidades específicas y puede ser ejecutado directamente.

## Ejemplo 1: Trabajador de Finca Rural (`example_finca_rural.json`)

**Características:**
- Trabajador que reside en el lugar de trabajo (finca)
- Auxilio de transporte **NO** aplica por residencia en lugar de trabajo
- Auxilio de transporte incluido (requiere validación de pacto)
- Salario variable con historial de 12 meses
- Modo PERIÓDICA

**Resultados Esperados:**
- SBL_GENERAL = $2,500,000 (salario base + comisiones + extras + bonificaciones + auxilio conectividad)
- SBL_VACACIONES = $2,200,000 (salario base + comisiones, excluyendo extras y auxilios)
- Cesantías = $2,500,000 (360 días)
- Intereses = $300,000 (tasa 12%)
- Prima = $1,250,000 (primer semestre completo)
- Total Liquidación Periódica = $4,050,000

**Validaciones Clave:**
- V003: Auxilio de transporte excluido correctamente por residencia en finca
- Alerta sobre auxilio de transporte (verificar si está pactado como salario)
- V007: Vacaciones excluidas en modo PERIÓDICA

**Comando para ejecutar:**
```bash
python -m liquidator.bin.liquidar --input examples/example_finca_rural.json --output examples/output_finca_rural.json --generate-pdf