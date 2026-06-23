# Diagnóstico técnico — liquidacion_cli

Fecha de revisión: 2026-06-09
Última auditoría de validación contra código vivo: 2026-06-09 (verificaciones reproducidas literalmente en sesión posterior; ver §6 Decisiones validadas)
Ruta revisada: `C:\Users\Jhond\Github\liquidacion_cli`
Ruta WSL equivalente: `/mnt/c/Users/Jhond/Github/liquidacion_cli`
Alcance: diagnóstico, contexto para diseño de plan y arquitectura de segundo cerebro, sin implementación.

## 1. Propósito evaluado

El objetivo es modernizar el proyecto para que un humano, operando una herramienta CLI local, pueda generar un documento de liquidación de nómina a partir de los datos necesarios de entrada. No se contempla API, llamada a LLM en la nube ni validación por terceros: el resultado se calcula y se entrega en la misma máquina del usuario único (Jhond).

Caso de uso canónico declarado: liquidar cesantías correspondientes al período 16 de noviembre de 2025 a 15 de junio de 2026 (211 días calendario). El sistema debe ser capaz, como mínimo, de:

1. Aceptar este período como entrada sin error de validación.
2. Calcular cesantías, intereses sobre cesantías, prima de servicios y demás prestaciones aplicables con la fórmula legal vigente.
3. Producir un documento verificable (JSON + Markdown + PDF) trazable a los parámetros, normas y reglas usadas.

Para ese propósito, el repositorio debería tener al menos:

1. Contrato de entrada claro y validado.
2. Motor de cálculo confiable y trazable.
3. Compliance legal que bloquee errores críticos (CRITICAL) o requiera override explícito (HIGH), con MEDIUM como advertencia.
4. Contrato de salida JSON/Markdown/PDF.
5. Plantillas documentales modernas y renderizables.
6. Tests estables, con el 100% de la suite pasando como criterio de cierre por fase.
7. Empaquetado limpio e instalable. Versión objetivo: v2.0 (cambios incompatibles permitidos, sin compromiso de retro-compatibilidad con v1.x).
8. Documentación coherente con el estado real del código.
9. Base de conocimiento local (segundo cerebro) que obligue a consultar código, parámetros, normas, pruebas y auditorías antes de calcular o generar documentos, sin dependencia de API externa. Si se requiere LLM de soporte, debe ser local (ollama, llama.cpp o similar).

Diagnóstico general: el proyecto tiene una base funcional parcial, pero actualmente no está listo como herramienta CLI confiable. Hay problemas críticos de empaquetado, tests rotos, sintaxis inválida, inconsistencias de cálculo, documentación desactualizada, ausencia de una base de conocimiento local estructurada y mezcla de código fuente con artefactos generados. La auditoría de validación contra código vivo confirmó los hallazgos principales y agregó precisiones documentadas en cada hallazgo y en §6.

---

## 2. Evidencia ejecutada

### 2.1 Estado del repositorio

Se verificó que la ruta existe y contiene el proyecto.

Hallazgos:

- No existe `.git`.
- No existe `.gitignore`.
- No existe `pyproject.toml`.
- No existe `MANIFEST.in`.
- No existe `liquidator/cli`.
- No existe `liquidator/tests/runner.py`.
- No existe directorio `output/`.
- No existe directorio `logs/`.
- No existe `AGENTS.md` ni `CLAUDE.md`.
- No existe `Contexto/KB_LLM/`.
- Sí existen:
  - `params/2025.json`
  - `params/normas.json`
  - `params/plazos.json`
  - `params/checklist.json`
  - `templates/comprobante_periodica.md`
  - `templates/comprobante_finiquito.md`
  - `config/default_config.yaml`
  - `config/logging_config.yaml`
  - `config/compliance_policies.yaml`
- Existe `.env` en la raíz con la clave `LIQUIDACION_ENCRYPTION_KEY` en texto plano (riesgo de seguridad, ver §3.14).

### 2.2 Inventario aproximado

Excluyendo ambientes virtuales, cachés, `htmlcov` y `__pycache__`, se detectaron aproximadamente:

- 211 archivos útiles.
- 107 archivos Python.
- 18.483 líneas Python.
- 34 archivos Markdown.
- 34 archivos JSON.
- 13 archivos PDF.
- 5 archivos YAML.
- 3 archivos de log.

Directorios principales:

- `liquidator/`
- `docs/`
- `params/`
- `scripts/`
- `templates/`
- `config/`
- `examples/`
- `legal_docs/`
- `audit/`
- `Contexto/`

### 2.3 Pruebas de compilación

Comando ejecutado:

```bash
python3 -m compileall -q liquidator bin scripts generate_liquidacion.py generar_varios.py test_encabezado.py
```

Resultado: falló con errores de sintaxis en:

```text
liquidator/output/markdown_generator.py
  File ".../liquidator/output/markdown_generator.py", line 7
    from datetime
                 ^
SyntaxError: invalid syntax

liquidator/params/params_versioning.py
  File ".../liquidator/params/params_versioning.py", line 6
    from datetime
                 ^
SyntaxError: invalid syntax

liquidator/tests/test_audit/test_trail_generator.py
  File ".../liquidator/tests/test_audit/test_trail_generator.py", line 9
    from datetime
                 ^
SyntaxError: invalid syntax

liquidator/tests/test_calculators/test_indemnizacion.py
  File ".../liquidator/tests/test_calculators/test_indemnizacion.py", line 8
    from datetime , timedelta
                  ^
SyntaxError: invalid syntax

liquidator/tests/test_compliance/test_override.py
  File ".../liquidator/tests/test_compliance/test_override.py", line 6
    from datetime
                 ^
SyntaxError: invalid syntax
```

Verificación adicional con `ast.parse`: total de archivos `.py` rotos: **5** (los mismos listados). El patrón es siempre el mismo: declaración `from datetime` (o `from datetime , timedelta`) sin usar import, o con coma en lugar de punto.

### 2.4 Pruebas ejecutadas

#### Test del motor principal

Comando:

```bash
PYTHONPATH=/mnt/c/Users/Jhond/Github/liquidacion_cli \
uv run --with pytest --with python-dateutil --with PyYAML --with jsonschema \
--with pydantic --with loguru --with click --with markdown --with Jinja2 \
pytest liquidator/tests/test_core/test_engine.py -q
```

Resultado:

```text
1 failed
```

Fallo:

```text
AssertionError: assert 'WARN' in {'GO', 'NO_GO', 'OVERRIDE_APPROVED'}
```

Interpretación: el motor devuelve `compliance_status = WARN`, pero el test espera un conjunto de estados que no incluye `WARN`. Ver §3.7 para análisis.

#### Test del generador JSON

Comando:

```bash
PYTHONPATH=/mnt/c/Users/Jhond/Github/liquidacion_cli \
uv run --with pytest --with python-dateutil --with PyYAML --with jsonschema \
--with pydantic --with loguru --with click --with markdown --with Jinja2 \
pytest liquidator/tests/test_output/test_json_generator.py \
liquidator/tests/test_calculators/test_sbl.py -q
```

Resultado:

```text
4 failed, 24 passed
```

Fallos principales:

```text
TypeError: JSONGenerator.__init__() takes 1 positional argument but 2 were given
```

Interpretación: los tests esperan un constructor con `schema_path`, pero la implementación actual no lo soporta.

#### Test de prestaciones

Comando:

```bash
PYTHONPATH=/mnt/c/Users/Jhond/Github/liquidacion_cli \
uv run --with pytest --with python-dateutil --with PyYAML --with jsonschema \
--with pydantic --with loguru --with click --with markdown --with Jinja2 \
pytest liquidator/tests/test_calculators/test_prestaciones.py -q
```

Resultado:

```text
3 failed, 48 passed
```

Fallos principales:

- `test_primer_semestre_completo`
- `test_casos_parametrizados[caso1-expected1]`
- `test_año_bisiesto_completo`

Interpretación: hay inconsistencias entre días calculados, cesantías y prima. Ver análisis caso por caso en §3.6.

#### Baseline global de la suite (auditoría)

Comando:

```bash
PYTHONPATH=. uv run --with pytest ... pytest liquidator/tests --collect-only -q
```

Resultado:

```text
173 tests collected, 13 errors in 2.69s
```

Interpretación: la suite completa reporta **13 errores de colección** no cubiertos por las pruebas ejecutadas arriba (afectan a archivos con sintaxis inválida y/o imports rotos en test_params, test_utils, test_validators, etc.). Las ejecuciones de §2.4 solo cubren ~58 tests. El estado real de la suite es peor de lo que sugieren los números parciales anteriores y debe tomarse como baseline para la Fase 1.

---

## 3. Debilidades críticas

### 3.1 No hay control de versiones real

No existe `.git`.

Impacto:

- No hay trazabilidad.
- No hay diffs.
- No hay ramas.
- No hay capacidad seria de rollback.
- No hay forma confiable de saber qué cambió entre versiones.
- Es riesgoso modernizar sin poder comparar estados.

Recomendación:

- Inicializar Git.
- Crear `.gitignore`.
- Crear estrategia de commits y releases.
- No commitear outputs generados, logs, ambientes virtuales ni cachés.

---

### 3.2 Hay outputs generados mezclados con código fuente

En la raíz hay archivos que parecen resultados de ejecución:

- `.coverage`
- `compensacion_pedro_franco.json`
- `finca_rural.json`
- `finca_rural_result.json`
- `generate_liquidacion.py`
- `generar_varios.py`
- `liquidacion.json`
- `liquidacion.pdf`
- `liquidacion_actualizada.json`
- `liquidacion_actualizada.pdf`
- `liquidacion_carta_sin_duplicado.json`
- `liquidacion_carta_sin_duplicado.pdf`
- `liquidacion_con_auxilio_transporte.json`
- `liquidacion_con_auxilio_transporte.pdf`
- `liquidacion_corregida.json`
- `liquidacion_corregida.pdf`
- `liquidacion_firmas_actualizadas.json`
- `liquidacion_firmas_actualizadas.pdf`
- `liquidacion_hildaliria.json`
- `liquidacion_hildaliria.pdf`
- `liquidacion_pedro_franco.json`
- `liquidacion_pedro_franco.pdf`
- `liquidacion_rural.json`
- `liquidacion_rural.txt`

Además existen logs:

- `audit/logs/audit_202511.log`
- `audit/logs/audit_202512.log`
- `audit/logs/audit_202606.log`
- `docs/audit/logs/audit_202511.log`

Impacto:

- El repositorio mezcla fuente, ejemplos, resultados y artefactos.
- Un modelo puede confundir outputs históricos con documentación o fixtures.
- El repo se vuelve más pesado y difícil de auditar.

Recomendación:

- Separar:
  - `examples/inputs/`
  - `examples/expected/`
  - `output/`
  - `artifacts/`
  - `logs/`
- Ignorar outputs generados en `.gitignore`.

---

### 3.3 Problemas de empaquetado e instalación

`setup.py` define entry points que no existen:

```python
entry_points={
    "console_scripts": [
        "settle=liquidator.cli.main:main",
        "settle-compliance=scripts.validate_compliance:main",
        "settle-update-params=scripts.update_params:main",
        "settle-generate-tests=scripts.generate_test_data:main"
    ]
}
```

Pero no existe `liquidator/cli`.

Además:

- No hay `pyproject.toml`.
- No hay `MANIFEST.in`.
- `package_data` apunta a `liquidator/templates/*`, pero las plantillas reales están en `templates/` raíz.
- Los ambientes virtuales existentes tienen estructura Windows:
  - `.venv/Scripts`
  - `liquidacion-env/Scripts`
  - no hay `bin/python` usable directamente desde WSL.

Impacto:

- `pip install -e .` puede fallar o instalar una CLI inexistente.
- El paquete no es portable.
- La experiencia de instalación no es moderna.

Recomendación:

- Migrar a `pyproject.toml`.
- Definir package correctamente.
- Crear un entry point real, por ejemplo:
  - `liquidacion=liquidator.cli:main`
  - o `python -m liquidator.cli`.
- Mover o corregir package data para que incluya plantillas reales.

---

### 3.4 Hay errores de sintaxis en producción y tests

Archivos críticos con sintaxis inválida:

- `liquidator/output/markdown_generator.py`
- `liquidator/params/params_versioning.py`
- `liquidator/tests/test_audit/test_trail_generator.py`
- `liquidator/tests/test_calculators/test_indemnizacion.py`
- `liquidator/tests/test_compliance/test_override.py`

Impacto:

- Generación Markdown no puede importar correctamente.
- Versionamiento de parámetros no puede importar correctamente.
- Parte de tests no se puede recolectar.
- No se puede confiar en CI hasta corregir esto.

Recomendación:

- Corregir imports.
- Agregar verificación mínima:
  - `python -m compileall liquidator`
- Agregar lint básico:
  - `ruff check`
  - o `flake8`.

---

### 3.5 El motor no valida entrada de forma consistente

`LiquidacionEngine.process_input()` usa `InputParser.parse()`, pero `parse()` solo acepta `dict` o `path` (firma verificada: `def parse(self, input_data: Union[Dict[str, Any], str])`).

`InputParser.validate_structure()` existe, pero no se observa invocación en el flujo principal del engine.

Además hay validadores separados que no parecen integrados:

- `liquidator/validators/input_validator.py`
- `liquidator/security/input_validator.py`
- `liquidator/security/data_sanitizer.py`

Impacto:

- El modelo puede generar documentos con datos incompletos.
- Errores legales pueden pasar.
- Datos sensibles pueden terminar en logs o salidas.
- No hay contrato de entrada robusto.

Recomendación:

- Definir un schema único de entrada, idealmente con Pydantic.
- Crear contrato claro para:
  - trabajador
  - empleador
  - fechas
  - salario
  - modo
  - tipo de contrato
  - auxilios
  - vacaciones
  - motivo de terminación
- Separar input legal de input de presentación.

---

### 3.6 El cálculo de cesantías parece subestimar períodos mayores a 360 días

En `PrestacionesCalculator.calculate_cesantias()` existe esta lógica:

```python
if dias_servicio >= 365 and not self.params.get("USAR_DIAS_REALES", False):
    dias_liquidar = Decimal("360")
else:
    dias_liquidar = Decimal(str(dias_servicio))
```

Ejemplo ejecutado con `examples/example_finca_rural.json`:

- Días servicio: 365
- SBL: 1.500.000
- Cesantías generadas: 1.500.000
- Fórmula esperada por el propio compliance:
  - `(1.500.000 × 365) / 360 = 1.520.833`

Resultado de compliance:

```text
V004 FAIL
Cesantías 1500000 != esperado 1520833
```

Ejemplo ejecutado con `examples/example_finiquito.json`:

- Días servicio: 977
- SBL: 2.950.000
- Cesantías generadas: 2.950.000
- Esperado por regla:
  - `(2.950.000 × 977) / 360 = 8.005.972`

Impacto:

- Error legal/comercial grave.
- El documento generado puede liquidar menos de lo debido.
- El compliance no bloquea porque los fallos no están marcados como blocking (ver §3.7).

Nota sobre el caso canónico (16-Nov-2025 a 15-Jun-2026, 211 días): el cap actual **no se activa** en este caso porque 211 < 365. Es decir, el motor PUEDE calcular este caso con la fórmula (SBL × 211) / 360. Sin embargo, el bug del cap sigue siendo real para cualquier período >= 365 días, y debe corregirse para que el sistema sea confiable como herramienta de uso general.

Auditoría adicional sobre el test `test_casos_parametrizados[caso1-expected1]`:

- Test espera: 715.208
- Motor produce: 715.704
- Comentario del propio test dice: `(1.423.500 × 181) / 360 = 715.704`
- Conclusión: el motor produce el valor consistente con la fórmula del comentario; el **valor esperado del test es el que está mal** (715.208 no sale de la fórmula documentada). El fix en este caso específico es actualizar el expected del test, no el código.

Recomendación:

- Definir política legal explícita. Si la regla aplicable es `SBL × días trabajados / 360`, eliminar el cap arbitrario de 360 para períodos mayores.
- Agregar el caso canónico (16-Nov-2025 a 15-Jun-2026, 211 días) como test golden con SBL=2.200.000 → cesantías esperadas = 1.289.444.
- Auditar y corregir los valores esperados de los tests existentes, separando claramente entre:
  - Tests cuyo expected es correcto y exponen un bug del motor (ej.: año bisiesto).
  - Tests cuyo expected es incorrecto y deben actualizarse (ej.: caso1 parametrizado).
- Agregar tests golden para:
  - períodos mayores a 360 días
  - años bisiestos
  - finiquitos largos
  - períodos parciales
  - caso canónico del usuario (211 días)

---

### 3.7 Compliance no bloquea fallos críticos

`params/checklist.json` define severidades:

- `CRITICAL`
- `HIGH`
- `MEDIUM`

Pero `ComplianceEngine` usa:

```python
"blocking": rule_info.get("blocking", False)
```

Como `blocking` no existe en el checklist (verificado: las reglas solo tienen campos `id`, `description`, `severity`, `rule_ref`), todos los fallos quedan como no bloqueantes.

Adicionalmente, el motor emite status `WARN` cuando una regla tiene `result == "WARN"` (compliance_engine.py L48-L59) y ese status no está permitido por el test del engine, lo que provoca el fallo descrito en §2.4.

Política de compliance mejorada (validada con el usuario, ver §6.4):

| Severidad | Comportamiento |
|---|---|
| CRITICAL | Bloquea la generación del documento. No se puede continuar sin cambio en el input o en los parámetros. |
| HIGH | Bloquea la generación salvo override explícito del usuario, que debe quedar registrado en auditoría con justificación. |
| MEDIUM | Advierte. El documento se genera con anotación visible. |
| LOW / INFO | Solo se registra en el log y en la auditoría. |

Mecánica recomendada:

- Mapear `severity` a `blocking` en cada regla de `params/checklist.json` (campo nuevo, no reemplazo).
- Mantener `severity` como metadato semántico y derivar `blocking` de ella por defecto: CRITICAL → True, HIGH → True (con override), MEDIUM/LOW → False.
- Si `enforce_compliance=True`, no generar documento final si hay fallos CRITICAL.
- Documentos bloqueados deben producir un artefacto `liquidacion_BLOQUEADA.{json,md,pdf}` con explicación de qué regla falló.
- Incluir estado de compliance visible en el documento (GO / WARN / NO_GO / OVERRIDE_APPROVED) en una sección fija.

Impacto de no actuar:

- V004 puede fallar y el sistema sigue generando documento.
- V010 puede fallar y el sistema sigue generando documento.
- El documento puede salir como `WARN`, no como documento bloqueado.

---

### 3.8 Output JSON tiene inconsistencias

`JSONGenerator.generate_json()` recibe `params`, pero no los usa.

Hardcodea (verificado en `liquidator/output/json_generator.py` L50-55):

```python
"SMMLV": 1423500,
"AUXILIO_TRANS": 200000,
"LIMITE_AUXILIO": 2847000,
"TASA_INT_CESANTIAS": 0.12,
"TOPE_INDEMNIZACION_SMMLV": 20,
```

Estos valores coinciden con `params/2025.json` al momento de la auditoría, pero el código NO los lee dinámicamente. Cualquier actualización de parámetros deja al generador desactualizado silenciosamente.

Además:

- `generate_output()` espera `calculation_result.get("alertas", {})`, pero el motor pasa `validaciones_y_alertas`. El motor sobreescribe `output["validaciones_y_alertas"]` (engine.py L97), así que en el flujo principal se disimula el error; pero cualquier uso directo de `JSONGenerator` fuera del motor entrega `alertas = {}` silenciosamente.
- Los tests esperan un constructor `JSONGenerator(schema_path)` con `schema_path`; la implementación actual solo acepta `self`.

Impacto:

- Parámetros desactualizados.
- Duplicación de constantes.
- Inconsistencia entre uso directo de `JSONGenerator` y uso vía motor.
- Dificultad para que un modelo genere documentos confiables.

Recomendación:

- Usar siempre parámetros cargados desde `params/`.
- Normalizar estructura de salida.
- Definir JSON schema de salida.
- Agregar tests de contrato.
- Inyectar `params` (no opcional) y eliminar las constantes hardcodeadas del generador.

---

### 3.9 Generación Markdown está rota

`liquidator/output/markdown_generator.py` no importa bien `datetime` (SyntaxError en L7, ver §2.3).

Además asume que siempre existen:

- `json_data["trabajador"]["nombre"]`
- `json_data["desglose"]["cesantias"]`
- `json_data["desglose"]["intereses_cesantias"]`
- `json_data["desglose"]["prima"]`

No maneja:

- Salida bloqueada por compliance.
- Documento de error.
- Campos opcionales.
- Validación previa del contexto.

Impacto:

- Si el modelo genera JSON válido pero con campos opcionales, Markdown puede fallar.
- No hay documento de error.
- No hay trazabilidad de por qué no se generó.

Recomendación:

- Corregir el SyntaxError.
- Crear generadores por estado:
  - documento completo
  - documento bloqueado
  - documento con advertencias
- Usar plantillas Jinja estrictas.
- Validar contexto antes de renderizar.

---

### 3.10 Generación PDF es frágil

`pdf_generator.py` tiene varios problemas:

1. Si no hay WeasyPrint, genera un `.txt` con comportamiento engañoso. Verificado:
   - L500 y L582: `output_path = output_path.with_suffix('.txt')` cuando WeasyPrint no está disponible.
   - L491: `self.logger.info(f"PDF generado exitosamente: {output_path}")` aunque el archivo sea `.txt` placeholder.
   - L736 (CLI): `print(f"PDF generado: {pdf_path}")` sin validar que sea PDF.

2. Tiene código muerto (verificado en L151):

   ```python
   return template
   for key, value in template_vars.items():
       ...
   ```

   Ese `return` hace que nunca se reemplacen placeholders después de esa línea.

3. La validación de salida (`validate_pdf_output`, L605) llega a leer el archivo como `.txt` (L637: `is_text_file = pdf_path.suffix.lower() == '.txt'`) en vez de fallar claramente.

Impacto:

- Se puede entregar un archivo que no es PDF.
- Mala experiencia para usuario final.
- Pérdida de confianza.

Recomendación:

- Si no hay WeasyPrint, devolver error claro.
- No generar `.txt` disfrazado de PDF.
- Agregar validación real del PDF:
  - header `%PDF-`
  - tamaño mínimo
  - número de páginas si es posible.

---

### 3.11 Parámetros legales existen, pero su integración es parcial

Sí existen como archivos de datos:

- `params/2025.json`
- `params/normas.json`
- `params/plazos.json`

Y como módulos (ubicación verificada):

- `liquidator/params/params_versioning.py` (roto por sintaxis, ver §3.4)
- `liquidator/params/params_validator.py` (implementación trivial: `return True`)
- `liquidator/legal/normas_repository.py` (existe, integración parcial)
- `liquidator/legal/plazos_manager.py` (existe, integración parcial)
- `liquidator/legal/topes_manager.py` (existe; sí usado por `indemnizacion_calculator.py` L14/L35)
- `liquidator/legal/recargos_manager.py` (existe; Decreto 2466/2025 implementado, `FECHA_APLICACION_RECARGO_DOMINICAL: 2025-07-01` en params/2025.json)

Matiz sobre la integración (auditoría):

- IndemnizaciónCalculator SÍ usa TopesManager (`from ..legal.topes_manager import TopesManager`).
- El engine principal SÍ carga `params/2025.json` mediante `ParamsLoader` (engine.py L13/L61).
- Lo que NO se respeta es la propagación aguas abajo: `JSONGenerator` y `MarkdownGenerator` duplican los parámetros en hardcode (§3.8).
- `ParamsValidator.validate()` retorna `True` sin validar nada.
- `NormasRepository` y `PlazosManager` están disponibles pero no se invocan en el flujo principal de cálculo de prestaciones.

Impacto:

- Hay información legal disponible, pero el flujo principal sigue usando lógica dispersa.
- Plazos y normas no se aprovechan plenamente para validar documentos.
- La actualización anual no está automatizada de forma confiable.

Recomendación:

- Integrar `NormasRepository` y `PlazosManager` al flujo de cálculo/compliance.
- Reemplazar validaciones hardcodeadas por reglas basadas en parámetros.
- Corregir `ParamsVersioning` y fortalecer `ParamsValidator` (validación real con schema).
- Centralizar el acceso a parámetros en una sola clase (`ParamsProvider` o similar) y eliminar todo hardcode en generadores.

---

### 3.12 Documentación desactualizada o contradictoria

Ejemplos verificados:

- `docs/validation_results.json` dice que faltan archivos que sí existen (26 menciones de "FAIL", 13 de "missing").
- `docs/health/system_health.json` afirma que `params/2025.json`, `params/normas.json`, `params/plazos.json` y `templates/` tienen `exists: False` — todos SÍ existen (verificado físicamente).
- `docs/code_quality_analysis.md` dice que se corrigieron problemas que siguen presentes.
- `README.md` promete "cumplimiento legal garantizado".
- `QWEN.md` habla de instalar desde PyPI y usar `settle`, pero el entry point real no existe.
- `examples/README_examples.md` espera SBL/Totales distintos a los que produce el motor.

Impacto:

- El modelo puede aprender documentación falsa.
- El usuario puede confiar en resultados no reales.
- Es difícil distinguir estado real vs estado documentado.

Recomendación:

- Regenerar documentación desde el código.
- Agregar tests de documentación (doctests, docstring validation).
- Evitar afirmaciones absolutas como "garantizado".
- Mantener README como contrato real.
- Corregir `docs/health/system_health.json` y `docs/validation_results.json` para que reflejen el estado real o eliminarlos y sustituirlos por una versión generada en CI.

---

### 3.13 Tests no son confiables

Hay tests que:

- No pasan (ver §2.4: 1+4+3 fallos en los archivos ejecutados).
- Esperan APIs inexistentes.
- No reflejan comportamiento real.
- No cubren documentos generados.
- No cubren contrato de entrada/salida.
- No cubren edge cases legales importantes.
- 13 archivos de test adicionales no se pueden recolectar por sintaxis inválida o imports rotos (baseline global: 173 tests collected, 13 errors, ver §2.4).

Ejemplos:

- `test_core/test_engine.py` falla por `WARN`.
- `test_output/test_json_generator.py` falla por constructor.
- `test_calculators/test_prestaciones.py` falla en cesantías/prima (1 caso expone bug del cap, 1 caso tiene expected value incorrecto en el propio test).
- Tests con sintaxis inválida no se pueden ejecutar.

Impacto:

- No hay red de seguridad.
- Una modernización puede romper más cosas sin saberlo.

Recomendación (DoD universal por fase — validado con el usuario, ver §6.6):

- **El 100% de la suite debe estar pasando** antes de cerrar cualquier fase.
- Primero estabilizar: corregir los 5 archivos con SyntaxError (§2.3) y resolver los 13 errores de colección.
- Crear tests golden con expected values verificados:
  - finca rural periódica
  - finiquito sin justa causa
  - salario variable
  - período parcial
  - año bisiesto
  - período mayor a 360 días
  - auxilio transporte excluido
  - vacaciones en finiquito
  - vacaciones por acuerdo mutuo
  - **caso canónico del usuario**: 16-Nov-2025 a 15-Jun-2026, 211 días, SBL=2.200.000, cesantías esperadas = 1.289.444
- Crear fixtures de expected JSON/Markdown/PDF en `examples/expected/`.
- Separar tests que exponen bugs reales del motor de tests que tienen expected value incorrecto (auditar y corregir el segundo grupo).

---

### 3.14 Seguridad y datos sensibles

Existe `.env` en el proyecto con variables:

- `LIQUIDACION_ENV=production`
- `LIQUIDACION_ENCRYPTION_KEY=5ca2e4b56c6e977d5c685796599c2673d7856e7354553064971b790692e04498` (clave de cifrado en texto plano)
- `LIQUIDACION_CONFIG_PATH=C:\Users\Jhond\Github\liquidacion_cli\config`
- `LIQUIDACION_DATA_PATH=C:\Users\Jhond\Github\liquidacion_cli`

No se exponen valores aquí más allá del hecho confirmado de que existe una clave de cifrado en el proyecto. **Esto ya es un incidente de seguridad**: cualquier `git init` seguido de `git add .` expone la clave.

Impacto:

- Si se sube a Git, exposición de secretos.
- Datos de trabajadores pueden quedar en logs, trails o outputs.
- No hay `.gitignore`.

Recomendación:

- Crear `.env.example` con valores placeholder.
- **Rotar la clave de cifrado actual** (asumir compromiso) antes de inicializar git.
- Nunca commitear `.env`.
- Sanitizar logs (no incluir salarios, nombres ni documentos en logs).
- No incluir documentos, nombres o documentos reales en repo.
- `.gitignore` debe incluir `.env`, `.venv/`, `liquidacion-env/`, `output/`, `artifacts/`, `logs/`, `audit/logs/*` (excepto `.gitkeep`), `__pycache__/`, `*.pyc`, `.coverage`, `htmlcov/`, `.mypy_cache/`, `.pytest_cache/`, `liquidacion*.{json,pdf,txt}`, `finca_rural*.json`, `compensacion_*.json`, `test_encabezado.py`, `generate_liquidacion.py`, `generar_varios.py`.

---

### 3.15 Arquitectura de documento generable es débil

Para el propósito "humano operando CLI genera este documento con input de datos necesarios", hoy falta:

- Contrato de entrada formal.
- Schema de salida formal.
- Plantilla documental central.
- Separación entre cálculo y documento.
- Estado de documento bloqueado/advertido.
- Evidencia legal por renglón.
- Auditoría integrada en el documento.
- Validación pre-render.
- Generación Markdown/PDF consistente.

Recomendación de arquitectura:

```text
input_schema/
  liquidacion_input.schema.json

domain/
  calculators/
  validators/
  legal_rules/

contracts/
  liquidacion_result.schema.json
  document_context.schema.json

document/
  templates/
    periodic.md.j2
    finiquito.md.j2
    blocked.md.j2
    warning.md.j2
  renderers/
    markdown.py
    pdf.py

cli/
  liquidar.py

params/
  economic/
  legal/
  deadlines/
```

Flujo ideal:

```text
input JSON/CLI
  -> validar input contra schema
  -> normalizar
  -> calcular prestaciones (usando params vigentes)
  -> validar legalmente (compliance con severidad→bloqueo)
  -> construir document_context
  -> renderizar Markdown
  -> renderizar PDF solo si NO_GO no está activo
  -> guardar JSON resultado
  -> guardar auditoría (incluye versión de params, reglas aplicadas, hash de input y output)
  -> devolver estado GO/WARN/NO_GO/OVERRIDE_APPROVED
```

---

## 4. Prioridad recomendada para modernizar

Cada fase tiene como **criterio de cierre (DoD) el 100% de los tests pasando**, conforme a la decisión validada (§6.6).

### Fase 0 — Higiene del repositorio y segundo cerebro mínimo

Esta fase es la base habilitante. Sin ella, cualquier cambio posterior es inseguro.

1. Inicializar Git (después de rotar la clave de cifrado del `.env`).
2. Crear `.gitignore` completo (ver §3.14).
3. Mover outputs generados a `output/` y `artifacts/` (ver §3.2).
4. Corregir los 5 archivos con SyntaxError (§2.3, §3.4).
5. Eliminar `liquidacion*.{json,pdf,txt}` y los scripts de un solo uso (`generate_liquidacion.py`, `generar_varios.py`, `test_encabezado.py`) de la raíz; los necesarios se mueven a `scripts/` con propósito claro.
6. Crear `Contexto/KB_LLM/` con notas mínimas (ver §5.3).
7. Crear `AGENTS.md` en la raíz con la jerarquía de verdad y las reglas de operación.
8. Definir jerarquía de verdad (§5.1).
9. Definir reglas de operación para agentes (§5.5).
10. Diseñar `scripts/check_kb_freshness.py` y `tests/test_kb_freshness.py`.

DoD Fase 0: `git init` exitoso, `git status` limpio tras un commit inicial, `python3 -m compileall liquidator` retorna 0, los 5 archivos corregidos, `AGENTS.md` y las 9 notas de `Contexto/KB_LLM/` creadas, 100% de la suite pasando (o tan cerca como sea posible sin tocar lógica de negocio — si quedan fallos preexistentes en lógica, se documentan y se trasladan a Fase 2).

### Fase 1 — Estabilizar y formalizar

1. Migrar `setup.py` a `pyproject.toml`.
2. Crear `liquidator/cli/main.py` con entry point real (`liquidacion=...` o `python -m liquidator.cli`).
3. Eliminar package_data incorrecto; mover plantillas a `liquidator/templates/` o ajustar referencias.
4. Definir input schema con Pydantic (modelo `LiquidacionInput`).
5. Definir output schema (JSON Schema para `liquidacion_result.json`).
6. Reemplazar constantes hardcodeadas en `JSONGenerator` por lectura de `params/2025.json`.
7. Corregir `JSONGenerator.__init__` para aceptar `schema_path`.
8. Arreglar `JSONGenerator` para usar `validaciones_y_alertas` consistentemente.
9. Corregir `params_versioning.py` y fortalecer `params_validator.py` (validación real con schema).
10. Corregir `markdown_generator.py` (SyntaxError + manejo de estado bloqueado/advertido).
11. Limpiar código muerto y fallback engañoso en `pdf_generator.py` (§3.10).
12. Actualizar `docs/health/system_health.json` y `docs/validation_results.json` para reflejar el estado real o eliminarlos y sustituirlos por un healthcheck generado en CI.
13. Crear el test del caso canónico (211 días) con SBL=2.200.000 → cesantías esperadas = 1.289.444.

DoD Fase 1: `pip install -e .` instala la CLI correctamente, `python -m liquidator.cli --help` muestra ayuda, todos los generadores (JSON/Markdown/PDF) producen archivos válidos para el caso canónico, 100% de la suite pasando.

### Fase 2 — Contrato legal y cálculo correcto

1. Resolver la ambigüedad del cap de cesantías (§3.6) con cita legal explícita.
2. Corregir la lógica de `calculate_cesantias` para que respete la fórmula legal acordada.
3. Auditar y corregir todos los expected values de los tests que estaban mal (ej.: test_casos_parametrizados[caso1]).
4. Implementar mapping `severity` → `blocking` en `params/checklist.json` (§3.7).
5. Implementar la lógica de `OVERRIDE_APPROVED` (override explícito del usuario con justificación registrada).
6. Integrar `NormasRepository` y `PlazosManager` al flujo de cálculo de prestaciones.
7. Agregar tests golden completos (§3.13).
8. Si en esta fase surge información sobre casos reales disponibles (ver §6.7), anexarlos a `Contexto/KB_LLM/02_parametros_2025.md` con cita de fuente.

DoD Fase 2: caso canónico (211 días) calculado correctamente, todos los golden tests pasando, ningún test expone bug en cálculo, 100% de la suite pasando.

### Fase 3 — Documento generable robusto

1. Crear contexto documental único (estructura `document_context` formal).
2. Separar cálculo de presentación (no mezclar `calculation_result` con `document_context`).
3. Crear plantillas Markdown/PDF modernas con Jinja2.
4. Manejar estados:
   - GO
   - WARN
   - NO_GO
   - OVERRIDE_APPROVED
5. Incluir evidencias legales por concepto (cita CST, ley, decreto) en cada renglón.
6. Validar documento antes de guardarlo (pre-render validation).
7. Generar documento bloqueado (`liquidacion_BLOQUEADA.{json,md,pdf}`) cuando el estado es NO_GO.
8. Renderizar PDF solo si el estado NO es NO_GO.
9. Auditoría JSON por ejecución (incluye versión de params, hash de input, hash de output, reglas aplicadas, warnings/overrides).

DoD Fase 3: el caso canónico genera los 3 archivos (JSON, Markdown, PDF) correctos, el caso bloqueado por NO_GO genera `liquidacion_BLOQUEADA.*` con explicación, 100% de la suite pasando.

### Fase 4 — Modernización para v2.0

1. Versión objetivo: v2.0 (semver, sin compromiso de retro-compatibilidad).
2. Pydantic en input y output (modelos formalizados).
3. Ruff/Black/Mypy como gate de CI.
4. CLI moderna con Typer o Click bien estructurado, `python -m liquidator.cli` y entry point `liquidacion`.
5. Generación PDF robusta con validación de header.
6. Auditoría JSON inmutable por ejecución.
7. Versionamiento de parámetros con verificación de freshness.
8. CHANGELOG actualizado a v2.0 con breaking changes documentados.
9. README reescrito para reflejar el estado real de v2.0 (no v1.0.0).

DoD Fase 4: `liquidacion --version` retorna `2.0.0`, CHANGELOG tiene entrada v2.0, README actualizado, CI ejecuta ruff + pytest + compileall, 100% de la suite pasando.

### Fase 5 (opcional, condicional) — Investigación de casos reales

Solo se ejecuta si en el trascurso de las fases 0-4 surge información sobre disponibilidad de casos reales (ver §6.7). No se ejecuta por defecto.

1. Investigar fuentes de casos reales (conceptos del Ministerio del Trabajo, jurisprudencia, casos contables de la operación del usuario).
2. Si se obtienen, anexarlos a `Contexto/KB_LLM/` con cita de fuente y anonimización.
3. Convertir cada caso real en un test golden adicional.

DoD Fase 5: si se ejecuta, al menos un caso real anexado con fuente citada y test golden derivado pasando.

---

## 5. Contexto para diseñar el plan en una nueva sesión: segundo cerebro y base de conocimiento local

Esta sección fue incorporada después del diagnóstico inicial para que una nueva sesión pueda diseñar un plan de modernización que no dependa solo de documentación estática, sino de una arquitectura de conocimiento capaz de mantener actualizado el contexto.

### 5.1 Principio rector

El sistema (humano + herramientas, incluyendo LLM local si se usa) no debe aprender liquidacion_cli desde README, docs antiguos o outputs generados. Debe operar con una jerarquía de verdad explícita y verificable.

Orden recomendado de confianza:

1. Código vivo: `liquidator/`, scripts y módulos activos.
2. Parámetros versionados: `params/2025.json`, `params/normas.json`, `params/plazos.json`.
3. Tests reales y resultados de ejecución.
4. Documentos legales fuente: `legal_docs/`.
5. Diagnósticos y auditorías: `Contexto/`, `audit/`.
6. Documentación general: `docs/`, `README.md`, `QWEN.md`, ejemplos.

Regla operativa:

Si la documentación contradice código, parámetros o tests, la documentación no debe usarse como verdad. Debe marcarse como desactualizada y el plan debe incluir corrección o archivo en `Archive/`.

### 5.2 No se recomienda fine-tuning como primera solución

Para este proyecto no es recomendable empezar por fine-tuning.

Razones:

- Los parámetros legales y económicos cambian.
- El riesgo principal es usar reglas desactualizadas.
- El fine-tuning puede fijar errores en el modelo.
- No resuelve contradicciones entre docs, código y params.
- Es más costoso y menos auditable que una base de conocimiento consultable.

La solución recomendada es una arquitectura de segundo cerebro basada en:

- Markdown versionado.
- Memoria persistente para reglas estables.
- Skills o instrucciones de proyecto.
- Retrieval por archivos.
- MCP filesystem restringido al repositorio (opcional).
- Tests y gates de validación.
- Auditoría periódica de frescura.

### 5.3 Arquitectura mínima del segundo cerebro

La arquitectura mínima debe permitir que un agente o un humano, en una nueva sesión, lea el contexto correcto antes de calcular, diseñar, corregir o generar documentos.

Estructura recomendada:

```text
liquidacion_cli/
  Contexto/
    KB_LLM/
      00_fuente_de_verdad.md
      01_reglas_calculo.md
      02_parametros_2025.md
      03_compliance_blocking.md
      04_schema_entrada.md
      05_schema_salida.md
      06_riesgos_modelo.md
      07_checklist_generacion_liquidacion.md
      08_arquitectura_segundo_cerebro.md
      09_caso_canonico_usuario.md
    prompts/
      prompt_generacion_liquidacion.md
      prompt_auditoria_antes_de_responder.md
      prompt_plan_modernizacion.md
  AGENTS.md
  scripts/
    check_kb_freshness.py
  tests/
    test_kb_freshness.py
```

La nota `09_caso_canonico_usuario.md` documenta el caso validado (16-Nov-2025 a 15-Jun-2026, 211 días, SBL=2.200.000, cesantías esperadas = 1.289.444) como referencia de cálculo que toda nueva sesión debe poder reproducir.

Opcionalmente, si se usa Obsidian o una metodología tipo vault:

```text
liquidacion_cli/
  SecondBrain/
    Projects/
      Liquidacion CLI.md
    Areas/
      Calculo Laboral/
        Cesantias.md
        Prima.md
        Vacaciones.md
        Auxilio Transporte.md
      Compliance/
        GO_WARN_NO_GO.md
        Reglas Bloqueantes.md
        Evidencia Legal.md
    Resources/
      Parametros 2025.md
      Normas y Plazos.md
      Templates.md
      Tests Golden.md
    Archive/
      Docs No Confiables.md
```

Obsidian es útil si se quiere una interfaz humana de notas conectadas, pero no es obligatorio. La condición necesaria es que el sistema pueda leer, buscar y verificar archivos Markdown/JSON/YAML dentro del repositorio.

### 5.4 Capas de conocimiento recomendadas

| Capa | Tipo | Ubicación sugerida | Función |
|---|---|---|---|
| Fuente de verdad estructural | Código y datos | `liquidator/`, `params/`, `legal_docs/`, `tests/` | Cálculos, reglas legales, parámetros y validaciones reales. |
| Conocimiento versionado | Markdown | `Contexto/KB_LLM/` | Reglas, decisiones, riesgos, checklist y arquitectura del segundo cerebro. |
| Memoria persistente | Hermes memory | Configuración de Hermes | Reglas estables del usuario/proyecto, por ejemplo: no confiar en docs sin contrastar. |
| Skill de proyecto | Hermes skill o repo skill | `skills/liquidacion-cli-kb/` | Flujo operativo para agentes que trabajan en liquidacion_cli. |
| Retrieval | Archivos, MCP filesystem restringido, Obsidian (opcional) | Repo o vault | Permitir búsqueda y lectura de contexto antes de responder. |
| Validación | Tests y scripts | `tests/`, `scripts/` | Impedir que el sistema genere cálculos o documentos inconsistentes. |

### 5.5 Reglas de operación que debe incorporar el plan

Toda nueva sesión que diseñe o ejecute modernización debe asumir estas reglas:

1. Antes de calcular, leer `params/2025.json`, `params/normas.json` y `params/plazos.json`.
2. Antes de confiar en una regla legal, buscar evidencia en `legal_docs/` o en el código que implementa la regla.
3. Antes de aceptar documentación, contrastarla contra código, params y tests.
4. No hardcodear SMMLV, auxilio de transporte, límites salariales, tasas o plazos.
5. No usar outputs generados como fuente de verdad.
6. No incluir nombres, documentos de identidad, salarios reales o datos sensibles en la KB.
7. No generar PDF si el estado de compliance es `NO_GO`.
8. No disfrazar `.txt` como PDF.
9. Separar claramente estados `GO`, `WARN`, `NO_GO` y `OVERRIDE_APPROVED`.
10. Cada documento generado debe poder auditar qué params, normas y reglas usó.
11. **Antes de aceptar como verdad cualquier afirmación del diagnóstico 2026-06-09, verificar contra código vivo** (este documento fue auditado el 2026-06-09; las correcciones están en §3.6, §3.7, §3.8, §3.11, §3.13 y §6).
12. Reproducir el caso canónico (211 días, 16-Nov-2025 a 15-Jun-2026) como primera prueba de cordura antes de cualquier cambio.

### 5.6 Flujo operativo recomendado para generación documental

El segundo cerebro debe soportar este flujo:

```text
1. Leer input.
2. Validar input contra schema.
3. Cargar params vigentes.
4. Consultar reglas de cálculo desde KB_LLM y código.
5. Calcular prestaciones.
6. Construir resultado estructurado.
7. Ejecutar compliance (severidad → bloqueo).
8. Si hay fallo CRITICAL, detener.
9. Si hay fallo HIGH, requerir override explícito del usuario.
10. Construir document_context.
11. Renderizar Markdown.
12. Renderizar PDF solo si estado != NO_GO.
13. Guardar JSON de resultado.
14. Guardar auditoría de fuentes usadas.
15. Actualizar o proponer actualización de KB si hubo cambio legal/paramétrico.
```

### 5.7 Prompt base que debe quedar disponible para agentes

El plan debe prever un prompt reutilizable con esta lógica:

```text
Antes de responder sobre liquidacion_cli:

1. Lee Contexto/diagnostico_liquidacion_cli_2026-06-09.md y verifica cada afirmación contra código vivo.
2. Lee Contexto/KB_LLM/00_fuente_de_verdad.md.
3. Lee Contexto/KB_LLM/01_reglas_calculo.md.
4. Lee Contexto/KB_LLM/09_caso_canonico_usuario.md (211 días, SBL=2.200.000, cesantías=1.289.444).
5. Consulta params/2025.json, params/normas.json y params/plazos.json.
6. Contrasta cualquier regla contra liquidator/ y tests.
7. Si docs contradice código o params, marca la contradicción.
8. No calcules con constantes hardcodeadas.
9. No generes documento final si compliance es NO_GO.
10. Incluye fuentes y versión de parámetros usadas.
11. Si falta evidencia, declara incertidumbre en vez de inventar.
```

### 5.8 Integración con Hermes Agent (u otro runtime local)

Para Hermes Agent u otro runtime local, la adaptación recomendada es:

A. Memoria persistente

Usar memoria solo para reglas estables, no para parámetros cambiantes.

Ejemplos de reglas memorizables:

- En liquidacion_cli, validar siempre contra código y params antes de aceptar documentación.
- No confiar en docs/README si contradicen código, params o tests.
- Priorizar riesgo legal/comercial sobre métricas técnicas.
- No incluir datos sensibles en KB, logs o repositorio.

B. Skill de proyecto

Crear una skill `liquidacion-cli-kb` cuando el flujo se estabilice. Debe contener:

- Fuentes de verdad.
- Flujo de cálculo.
- Checklist de compliance.
- Checklist de generación documental.
- Riesgos conocidos.
- Comandos de verificación.
- Criterios de aceptación.

C. LLM local (si se usa)

Restricción validada: no se usará API externa para cálculo ni para inferencia. Si se requiere LLM en el flujo:

- Opciones: ollama, llama.cpp, vLLM local, LM Studio, Jan, o cualquier servidor OpenAI-compatible que corra en la misma máquina.
- Modelos sugeridos (referencia, no compromiso): Llama 3.x, Qwen 2.5, Mistral, Phi-3 según capacidad del hardware.
- El plan debe documentar cómo invocar el modelo local desde el flujo (ej.: cliente OpenAI-compatible apuntando a `http://localhost:11434/v1`).

D. MCP o retrieval

Opcional pero recomendable para escalar:

- MCP filesystem restringido al repositorio (`/mnt/c/Users/Jhond/Github/liquidacion_cli`).
- MCP search o index si la KB crece.
- Obsidian vault si se quiere interfaz humana de notas conectadas.

Configuración conceptual:

```yaml
mcp_servers:
  liquidacion_fs:
    command: npx
    args:
      - -y
      - @modelcontextprotocol/server-filesystem
      - /mnt/c/Users/Jhond/Github/liquidacion_cli
```

Nota: MCP debe restringirse al proyecto o al vault. No exponer todo el home del usuario ni documentos sensibles.

### 5.9 Criterios de aceptación para el plan de segundo cerebro

El plan diseñado en una nueva sesión debe incluir, como mínimo:

- Definición de fuentes de verdad.
- Estructura de carpetas para `Contexto/KB_LLM/`.
- Contenido mínimo de cada nota de KB.
- Reglas de precedencia entre código, params, docs y auditorías.
- Diseño de `AGENTS.md` o `CLAUDE.md`.
- Diseño de prompt base para agentes.
- Diseño de checklist antes de calcular.
- Diseño de checklist antes de generar documento.
- Diseño de auditoría de fuentes usadas.
- Diseño de script o test de frescura de KB.
- Riesgos de MCP/Obsidian/RAG y decisión justificada.
- Plan de migración progresiva sin romper el flujo actual.
- Caso canónico del usuario documentado en `09_caso_canonico_usuario.md` y reproducible desde línea de comandos.

### 5.10 Riesgos que el plan debe controlar

| Riesgo | Impacto | Mitigación |
|---|---|---|
| KB desactualizada | El sistema reproduce reglas viejas. | Script de frescura y revisión contra params/código. |
| Docs contradicen params | Cálculos erróneos. | Jerarquía de verdad y auditoría documental. |
| Fine-tuning prematuro | Errores fijos en el modelo. | Usar RAG/KB antes de fine-tuning. |
| MCP demasiado amplio | Exposición de datos sensibles. | Restringir rutas permitidas al proyecto. |
| Obsidian sin estructura | Notas pasivas y difíciles de consultar. | Frontmatter, tags, wikilinks y prompts de mantenimiento. |
| Tests débiles | El sistema rompe cálculos sin detectarlo. | Tests golden, gates de compliance y DoD = 100% pasando. |
| Outputs generados en repo | Confunden al modelo. | `.gitignore`, carpetas `output/` y `artifacts/`. |
| Datos sensibles en KB | Riesgo legal y de privacidad. | Prohibir nombres, documentos, salarios reales y `.env`. |
| **.env con clave en texto plano** | Incidente de seguridad si se hace commit. | Rotar clave antes de `git init`, mover a `.env.example`. |
| **Sin validación externa y usuario único** | Un error del usuario se propaga sin detección externa. | Tests exhaustivos, auditoría inmutable, alertas de compliance, golden tests firmados con hash. |
| **Dependencia de LLM externo** | Falla el principio de "infraestructura local". | Forzar uso de LLM local o ejecutar sin LLM, solo KB + reglas. |
| **Falta de datos reales** | Tests sintéticos podrían no cubrir edge cases legales. | Fase 5 opcional para investigación; documentar asunciones en KB. |
| **Documento diagnóstico aceptado como verdad** | Una nueva sesión hereda errores del diagnóstico. | Regla operativa §5.5.11: siempre verificar contra código vivo. |

### 5.11 Decisión recomendada

La decisión recomendada para el plan es:

Construir primero una base de conocimiento local, pequeña y verificable dentro del repositorio. Después integrar Hermes memory/skills y, solo si el volumen de conocimiento lo justifica, MCP u Obsidian. No iniciar con fine-tuning ni con RAG vectorial complejo. Si se requiere LLM, debe ser local.

Esta decisión reduce más rápido el riesgo legal/comercial porque obliga al sistema a consultar fuentes actualizadas y bloquea contradicciones antes de generar documentos.

La línea de版本 objetivo es **v2.0** (validada, ver §6.5), con cambios incompatibles permitidos.

---

## 6. Decisiones de producto validadas (2026-06-09)

Esta sección registra las decisiones tomadas con el usuario durante la auditoría de validación. Cualquier nueva sesión debe partir de estas decisiones como inamovibles salvo que el usuario las revoque explícitamente.

### 6.1 Tipo de producto

El sistema es una **herramienta CLI local operada por un humano** (no API, no servicio web). El usuario único es **Jhond**, sin validación externa por terceros. La confiabilidad se garantiza por tests, auditoría interna y trazabilidad de fuentes, no por revisión humana externa.

Implicaciones:
- No hay endpoints REST, ni clientes HTTP, ni autenticación multiusuario.
- La salida es un archivo en disco (JSON + Markdown + PDF) más un log de auditoría.
- El usuario revisa cada liquidación antes de usarla; el sistema no se auto-aprueba.

### 6.2 Caso de uso canónico

Caso declarado: liquidar cesantías correspondientes al período **16 de noviembre de 2025 a 15 de junio de 2026** (211 días calendario).

Datos de referencia para el golden test:

- `fecha_ingreso`: 2025-11-16
- `fecha_corte`: 2026-06-15
- `modo`: PERIÓDICA
- SBL de referencia: 2.200.000 COP
- Cesantías esperadas: 1.289.444 COP (= 2.200.000 × 211 / 360, redondeado al entero)
- Prima: se reparte entre H2 2025 (45 días) y H1 2026 (165 días)

Este caso es el primer test de cordura que cualquier nueva sesión debe poder ejecutar y verificar. Si este caso no se calcula correctamente, el sistema no está listo.

### 6.3 Infraestructura

**Local, sin API**. El cálculo se hace en la misma máquina del usuario. Si se usa un LLM de soporte, debe ser local:

- Opciones: ollama, llama.cpp, vLLM local, LM Studio, Jan, o servidor OpenAI-compatible en localhost.
- No se contemplan OpenAI API, Anthropic API, Google API ni ningún servicio comercial.
- MCP, si se usa, debe correr en local y restringirse al repo.

### 6.4 Política de compliance mejorada

No hay política de negocio diferente a la propuesta; la propuesta del diagnóstico es aceptable e incluso mejorable. Política adoptada:

| Severidad | Comportamiento |
|---|---|
| CRITICAL | Bloquea. No se genera documento. Se produce `liquidacion_BLOQUEADA.{json,md,pdf}` con explicación. |
| HIGH | Bloquea salvo override explícito del usuario con justificación registrada en auditoría. |
| MEDIUM | Advierte. Documento se genera con anotación visible. |
| LOW / INFO | Solo se registra en log y auditoría. |

Implementación: campo `blocking` en cada regla de `params/checklist.json`, derivado por defecto de `severity`.

### 6.5 Versión objetivo

**v2.0**. Se siguen las reglas de Semantic Versioning, pero con cambios incompatibles permitidos (no hay compromiso de retro-compatibilidad con v1.x). El CHANGELOG debe documentar explícitamente los breaking changes.

### 6.6 Criterio de cierre (DoD) por fase

**100% de los tests pasando** al cierre de cada fase. Esto incluye:

- 0 errores de colección.
- 0 fallos de aserción.
- Todos los golden tests (incluido el caso canónico) verdes.
- CI ejecuta: `python3 -m compileall liquidator` + `ruff check` + `pytest liquidator/tests -q`.

No se acepta cerrar una fase con tests rojos, aunque sean tests preexistentes. Si un test preexistente expone un bug real, ese bug se corrige en la fase actual; si el test tiene un expected value incorrecto, se corrige el test con justificación documentada.

### 6.7 Disponibilidad de casos reales

No se tienen casos reales a disposición en este momento. Se permite incluir una **fase opcional (Fase 5)** para investigar disponibilidad de casos reales (conceptos del Ministerio del Trabajo, jurisprudencia, casos contables propios), pero:

- Esta fase no es bloqueante.
- No se ejecuta por defecto.
- Si se ejecuta y se obtienen casos, se anexan a `Contexto/KB_LLM/` con cita de fuente y anonimización, y se convierten en golden tests adicionales.

### 6.8 Definición de "Done" para el plan completo

El plan completo se considera "Done" cuando:

1. v2.0 está publicada.
2. El caso canónico (§6.2) se calcula correctamente y genera los 3 archivos esperados.
3. La suite completa de tests pasa al 100%.
4. `AGENTS.md` y `Contexto/KB_LLM/` existen y son mantenibles.
5. El usuario (Jhond) ha ejecutado al menos 3 liquidaciones reales con la nueva versión y los resultados coinciden con cálculos hechos manualmente o con otra herramienta de referencia.
6. El CHANGELOG documenta los breaking changes de v1.x a v2.0.

### 6.9 Perfil del usuario

- Usuario único: Jhond.
- No hay validación externa: ni contador, ni abogado, ni auditor revisa los resultados automáticamente.
- Implicación: la confiabilidad debe construirse en el sistema mismo, no en una segunda opinión humana externa.
- Mecanismos compensatorios obligatorios:
  - Tests exhaustivos (golden + casos borde + caso canónico).
  - Auditoría inmutable con hash por ejecución.
  - Compliance que bloquea errores graves.
  - Trazabilidad de fuentes (params, normas, reglas usadas) en cada documento generado.
  - Documento bloqueado explícito cuando hay NO_GO, en vez de salida silenciosa.

---

## 7. Conclusión

El proyecto tiene material aprovechable: calculadores, CLI, ejemplos JSON, plantillas Markdown/PDF, parámetros 2025, normas, plazos y tests. Sin embargo, hoy está más cerca de un prototipo avanzado con outputs generados que de una herramienta CLI confiable para v2.0.

Antes de pedirle al sistema que genere documentos, conviene estabilizar en este orden:

1. Higiene y control de versiones (Fase 0): corregir sintaxis, crear `.gitignore`, mover outputs, rotar clave de cifrado del `.env`, crear `Contexto/KB_LLM/` y `AGENTS.md`.
2. Estabilización y formalización (Fase 1): `pyproject.toml`, CLI real, schemas Pydantic, generadores consistentes.
3. Cálculo legal correcto (Fase 2): resolver el cap de cesantías, integrar `NormasRepository`/`PlazosManager`, mapping severidad→bloqueo.
4. Documento robusto (Fase 3): documento bloqueado, evidencia legal por renglón, validación pre-render.
5. v2.0 (Fase 4): empaquetado moderno, CI con gates, CHANGELOG actualizado.
6. Investigación de casos reales (Fase 5, opcional): solo si surgen casos durante el desarrollo.

Caso canónico de validación continua: liquidar cesantías 16-Nov-2025 a 15-Jun-2026 con SBL=2.200.000 → cesantías esperadas = 1.289.444. Este caso debe ser reproducible desde la línea de comandos en cada fase y debe pasar al 100% para considerar la fase cerrada.

Conclusión corta: el proyecto es recuperable. La auditoría contra código vivo (2026-06-09) confirmó la mayor parte del diagnóstico original, agregó precisiones (ubicación correcta de módulos, Indemnización sí usa TopesManager, motor sí carga params, baseline de 173 tests con 13 errores de colección, caso de test con expected value incorrecto, incidente de seguridad del `.env`) y cerró 9 decisiones de producto que una nueva sesión necesita para diseñar el plan sin suposiciones. El DoD universal del 100% de tests pasando, combinado con la infraestructura local-only y el caso canónico como prueba de cordura continua, debe ser el ancla del plan de modernización a v2.0.
