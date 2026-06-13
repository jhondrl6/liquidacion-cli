

# Planificación técnica, legal y operativa (Versión corregida)

# 1) Visión general del producto

Herramienta CLI que, a partir de datos del trabajador y periodos, calcula prestaciones causadas en un **periodo periódico** (no finiquito) y genera:

* Un **JSON** estructurado (compatible para ingestión por agentes).
* Un **PDF/MD** imprimible (Comprobante / Soporte de Pago Periódico).
* Registro de normas aplicadas en cada renglón (para auditoría legal).

Requisitos legales clave: uso de SBL, base 360 días para cesantías/prima/intereses; vacaciones con base 720; tasa intereses 12% anual; auxilio de transporte solo si corresponde y límite 2 SMMLV; pago inmediato en caso de finiquito (Art.65 CST) — todo documentado en las fuentes anexas.

---

# 2) Entradas (CLI flags / formato JSON de entrada)

El agente debe aceptar **dos modos**: `PERIODICA` y `FINIQUITO`. Para tu caso pedimos `PERIODICA`.

Campos de entrada (CLI flags `--` o JSON):

* `--modo` (string) : `"PERIÓDICA"` | `"FINIQUITO"`
* `--fecha_ingreso` (YYYY-MM-DD)
* `--fecha_corte` (YYYY-MM-DD)  ← para liquidación periódica, fecha final del periodo a liquidar
* `--salario_mensual` (int, COP) — salario base mensual pactado
* `--salarios_historicos` (opt list[YYYY-MM, valor]) — para promedios si salario variable
* `--comisiones_promedio_mensual` (float) — si aplica
* `--horas_extras_promedio_mensual` (float) — valor monetario promedio
* `--bonificaciones_promedio_mensual` (float)
* `--reside_en_lugar_trabajo` (bool) — **TRUE** en este caso (finca)
* `--auxilio_transporte` (int) — si la empresa reconoce en vez de transporte
* `--dias_vacaciones_pendientes` (int)
* `--tipo_contrato` : `"indefinido"` | `"fijo"`
* `--motivo_terminacion` (solo para FINIQUITO)
* `--salario_pendiente` (float) — suma de salarios devengados no pagados (si aplica)
* `--salario_pendiente_dias` (int)
* `--moneda` (default: "COP")
* `--enforce-compliance` (bool, default true) — si true el proceso bloqueará la generación final en caso de NO_GO
* `--compliance-policy` (`lenient`|`standard`|`strict`) — determina si warnings bloquean
* `--human-override` (opcional) — para permitir bypass con justificación
* `--operator-id` (string, opcional) — identificador del operador que autoriza override
* `--override-reason` (string, opcional) — justificación del override

Formato de entrada JSON ejemplo:

```json
{
  "modo":"PERIÓDICA",
  "fecha_ingreso":"2024-11-16",
  "fecha_corte":"2025-11-15",
  "salario_mensual":2000000,
  "reside_en_lugar_trabajo": true,
  "auxilio_conectividad": 200000,
  "comisiones_promedio_mensual": 0,
  "horas_extras_promedio_mensual": 0,
  "dias_vacaciones_pendientes": 0,
  "tipo_contrato":"indefinido",
  "enforce-compliance": true,
  "compliance-policy": "standard"
}
```

---

# 3) Parámetros oficiales / constantes (actualizables)

Hard-code inicial (2025) pero **cargar desde archivo de parámetros** con posibilidad de actualización anual:

* `SMMLV_2025 = 1423500`
* `AUXILIO_TRANS_2025 = 200000`
* `LIMITE_AUXILIO = 2 * SMMLV_2025`  (2 SMMLV)
* `TASA_INT_CESANTIAS = 0.12`
* `DIAS_BASE = 360.0` (para cesantías / prima)
* `VACACIONES_DENOM = 720.0` (para vacaciones)
* `REDONDEO = 0` (redondear a pesos)
* `TOPE_INDEMNIZACION_SMMLV = 20` (Art. 64 CST)
* `FECHA_APLICACION_RECARGO_DOMINICAL = "2025-07-01"` (Ley 2466/2025)

(Estos valores y su referencia normativa están en los anexos). 

---

# 4) Lógica de cálculo — reglas y fórmulas (con sustentos)

## 4.1 Determinar SBL (Base de Liquidación)

1. **SBL_GENERAL mensual** = `salario_mensual + comisiones_promedio_mensual + horas_extras_promedio_mensual + bonificaciones_promedio_mensual`.
2. **SBL_VACACIONES mensual** = `salario_mensual + comisiones_promedio_mensual` (excluyendo horas extras, recargos y auxilio de transporte/conectividad).
3. **Auxilio**:

   * Si `reside_en_lugar_trabajo == true` → **NO** incluir auxilio de transporte (porque el trabajador vive en la finca). 
   * **Advertencia**: El auxilio de transporte solo debe sumarse al SBL_GENERAL si está explícitamente pactado como parte del salario habitual. Si no está pactado, debe tratarse como un beneficio no constitutivo de salario y registrarse como alerta en el output.
4. Si salarios variables: SBL debe calcularse como promedio de los últimos 12 meses para Cesantías y para indemnización (jurisprudencia CSJ 2025). 

## 4.2 Días a liquidar

`DIAS_SERVICIO = (fecha_corte - fecha_ingreso).days + 1`
En cálculos usar **DIAS_BASE = 360** (base legal para fraccionamientos).

## 4.3 Fórmulas

* **Cesantías**:
  `Cesantias = (SBL_GENERAL * DIAS_SERVICIO) / 360`
  (Art. 249-250 CST). 
* **Intereses sobre cesantías**:
  `Intereses = (Cesantias * DIAS_SERVICIO * TASA_INT_CESANTIAS) / 360` (Ley 50/1990, tasa 12%). 
* **Prima de servicios (fracción semestre)**:
  `Dias_Prima = días correspondientes al semestre en curso`
  `Prima = (SBL_PRIMA * Dias_Prima) / 360` (Art.306 CST). Use SBL_PRIMA = promedio semestral o SBL_GENERAL según variable. 
* **Vacaciones (solo si se compensa en dinero / para finiquito)**:
  `Vacaciones = (SBL_VACACIONES * DIAS_VACACIONES_ACUMULADOS) / 720`
  *Nota*: En modo PERIÓDICA, las vacaciones no deben pagarse, solo acumularse. Se incluirán únicamente en modo FINIQUITO.
* **Salario pendiente**:
  `Salario_pendiente = salario_diario * dias_salario_pendiente + recargos_pendientes`
* **Total Periodica**: suma de Cesantías (a consignar), Intereses (a pagar), Prima (a pagar). (En modo PERIÓDICA no incluir indemnización ni vacaciones compensadas).

## 4.4 Reglas legales / validaciones

* Si `tipo_contrato == "prestación_servicios"` → abortar y mostrar error (no aplica prestaciones). 
* Si `reside_en_lugar_trabajo == true` → `auxilio_transporte` **NO** aplica; registrar alerta en output. 
* Verificar tope salarial para auxilio: solo si SBL ≤ LIMITE_AUXILIO.
* **Validación de recargo dominical**: Aplicar recargo del 80% solo si el periodo incluye fechas posteriores o iguales a `FECHA_APLICACION_RECARGO_DOMINICAL` (1-Jul-2025). Para periodos anteriores, usar el recargo vigente antes de esa fecha.
* **Validación de plazos de pago**: Cada prestación debe incluir un campo `plazo_pago_legal` con la fecha límite exacta según normativa:
  - Cesantías: consignar antes del 14 de febrero del año siguiente.
  - Intereses sobre cesantías: pagar antes del 31 de enero del año siguiente.
  - Prima de servicios: pagar en dos pagos, último día de junio y diciembre.
* **Validación de tope de indemnización**: Para cálculos de indemnización (en modo FINIQUITO), aplicar tope de 20 SMMLV: `SBL_INDEMN = min(SBL_GENERAL, 20 * SMMLV)`.

---

# 5) Formato de salida — JSON (esquema)

Salida principal: `liquidacion_periodica.json` (estructura):

```json
{
  "meta": {
    "modo":"PERIÓDICA",
    "fecha_generacion":"2025-11-16T12:00:00",
    "fecha_corte":"2025-11-15",
    "fecha_ingreso":"2024-11-16",
    "moneda":"COP",
    "params_version":"2025-10-31",
    "input_hash":"sha256:abcd...",
    "output_hash":"sha256:ef01...",
    "generator_version":"1.0.0"
  },
  "trabajador": {
    "nombre":"",
    "documento":"",
    "tipo_contrato":"indefinido",
    "reside_en_lugar_trabajo": true
  },
  "parametros": {
    "SMMLV":1423500,
    "AUXILIO_TRANS":200000,
    "LIMITE_AUXILIO":2847000,
    "TASA_INT_CESANTIAS":0.12,
    "DIAS_BASE":360,
    "TOPE_INDEMNIZACION_SMMLV":20,
    "FECHA_APLICACION_RECARGO_DOMINICAL":"2025-07-01"
  },
  "desglose": {
    "SBL_GENERAL": 2200000,
    "SBL_VACACIONES": 2000000,
    "cesantias": {
      "valor":2200000,
      "dias_liquidados":360,
      "plazo_pago_legal":"2026-02-14",
      "norma":"Art.249-250 CST"
    },
    "intereses_cesantias":{
      "valor":264000,
      "dias_liquidados":360,
      "plazo_pago_legal":"2026-01-31",
      "norma":"Ley 50/1990 Art.99"
    },
    "prima":{
      "valor":1100000,
      "dias_liquidados":180,
      "plazo_pago_legal":"2025-12-31",
      "norma":"Art.306-308 CST"
    },
    "vacaciones":{
      "valor":0,
      "dias_liquidados":0,
      "norma":"Arts.186-192 CST",
      "nota":"No aplica en modo PERIÓDICA, solo en FINIQUITO"
    }
  },
  "total_liquidacion_periodica": 3564000,
  "validaciones_y_alertas": {
    "auxilio_transporte_excluido":"Residencia en el lugar de trabajo (Finca).",
    "auxilio_conectividad_advertencia":"Verificar si está pactado como parte del salario habitual.",
    "recargo_dominical_aplicado":"No aplica (periodo anterior a 2025-07-01).",
    "nota_adicional":"Revisar horas extras y comisiones para SBL si son variables."
  },
  "normas_aplicadas":[
    "Art.249-250 CST",
    "Ley 50/1990 Art.99",
    "Art.306-308 CST",
    "Art.65 CST",
    "Art.64 CST",
    "Art.192 CST",
    "Ley 2466/2025"
  ],
  "compliance_report": {
    "compliance_status":"GO",
    "summary": {
      "passed": 25,
      "warnings": 3,
      "failures": 0
    },
    "checks":[
      {
        "id":"V001",
        "description":"Parametros oficiales 2025 presentes y consistentes",
        "result":"PASS",
        "evidence":"SMMLV=1423500 matches params/2025.json",
        "rule_ref":["Decreto 1572/2024"]
      },
      {
        "id":"V002",
        "description":"Contrato válido",
        "result":"PASS",
        "evidence":"Tipo de contrato es indefinido",
        "rule_ref":["Art. 23 CST"]
      },
      {
        "id":"V003",
        "description":"Auxilio transporte aplicado correctamente",
        "result":"PASS",
        "evidence":"Auxilio excluido por residencia en lugar de trabajo",
        "rule_ref":["CHECKLIST: Auxilio Transporte Finca Rural"]
      },
      {
        "id":"V004",
        "description":"Fórmulas de cesantías correctas",
        "result":"PASS",
        "evidence":"Cálculo coincide con fórmula legal",
        "rule_ref":["Art. 249-250 CST"]
      },
      {
        "id":"V005",
        "description":"Intereses de cesantías tasa correcta",
        "result":"PASS",
        "evidence":"Tasa 12% aplicada correctamente",
        "rule_ref":["Ley 50/1990 Art.99"]
      },
      {
        "id":"V006",
        "description":"Prima semestre proporcional",
        "result":"WARN",
        "evidence":"Periodo no coincide exactamente con semestre",
        "rule_ref":["Art.306-308 CST"]
      },
      {
        "id":"V007",
        "description":"Vacaciones excluidas en periódica",
        "result":"PASS",
        "evidence":"Vacaciones no incluidas en modo PERIÓDICA",
        "rule_ref":["Arts.186-192 CST"]
      },
      {
        "id":"V008",
        "description":"Plazos de pago documentados",
        "result":"PASS",
        "evidence":"Todas las prestaciones incluyen plazo_pago_legal",
        "rule_ref":["Art.65 CST", "Ley 50/1990 Art.99"]
      },
      {
        "id":"V009",
        "description":"Sustento legal presente",
        "result":"PASS",
        "evidence":"Cada renglón incluye referencia normativa",
        "rule_ref":["CHECKLIST: Sustento Legal"]
      },
      {
        "id":"V010",
        "description":"Hashes y versionamiento",
        "result":"PASS",
        "evidence":"Incluye params_version, input_hash, output_hash",
        "rule_ref":["CHECKLIST: Trazabilidad"]
      }
    ],
    "blocking_failures":[],
    "params_version":"2025-10-31",
    "timestamp":"2025-11-02T07:25:00-05:00",
    "input_hash":"sha256:abcd...",
    "output_hash":"sha256:ef01...",
    "operator_action": {
      "action":"auto",
      "operator_id":null,
      "justification":null
    }
  }
}
```

* Cada renglón incluye `norma` o `referencia`, `dias_liquidados` y `plazo_pago_legal` para trazabilidad. 
* Se han añadido campos de auditoría: `params_version`, `input_hash`, `output_hash`, `generator_version`.
* Se incluye `compliance_report` con el resultado de las validaciones.

---

# 6) Salida imprimible — Formato de Soporte (MD/PDF)

* Plantilla Markdown con:

  * Datos del empleador/trabajador.
  * Periodo liquidado.
  * Tabla de desglose (Cesantías, Intereses, Prima, Total).
  * Declaración de recepción / nota sobre consignación (Cesantías) y plazos legales (Fechas: consignación e intereses).
  * Firma (empleador / trabajador).
* Generar PDF usando `wkhtmltopdf` o `weasyprint` (dependencia opcional).

Plantilla y contenido de ejemplo en el anexo ya provisto (tomar como referencia). 

---

# 7) UX CLI — comandos y flags propuestos

* `liquidar --input input.json --output out.json`
* `liquidar --modo PERIODICA --fecha_ingreso 2024-11-16 --fecha_corte 2025-11-15 --salario_mensual 2000000 --reside_en_lugar_trabajo true --auxilio_transporte 200000 --out out.json`
* `liquidar --test-run` → ejecuta suite de validación interna y muestra logs.
* `liquidar --generate-pdf out.json` → genera PDF del comprobante.
* `liquidar --compliance-check-only input.json` → ejecuta solo las validaciones de cumplimiento y genera el reporte sin calcular la liquidación.

Salida CLI debe ser *machine-readable* (JSON) y human-friendly (tabla en consola + link a PDF si generado).

---

# 8) Estructura de proyecto sugerida (módulos)

```
liquidacion_cli/
├─ bin/
│  └─ liquidar  (entrypoint)
├─ liquidator/
│  ├─ __init__.py
│  ├─ core.py            # funciones principales y flow engine
│  ├─ sbl.py             # cálculos y promedios SBL
│  ├─ formulas.py        # cesantias, intereses, prima, vacaciones
│  ├─ validators.py      # validaciones legales
│  ├─ params.py          # constantes y loader de parámetros (yaml/json)
│  ├─ output.py          # JSON and PDF/MD render
│  ├─ compliance_checker.py  # módulo de control previo
│  └─ tests/
│     ├─ test_examples.py
│     ├─ test_edgecases.py
│     └─ test_compliance.py
├─ docs/
│  └─ spec.md
├─ params/
│  └─ 2025.json
├─ audit/               # directorio para logs de auditoría
├─ examples/
│  └─ example_input.json
└─ README.md
```

---

# 9) Pseudocódigo / flujo de implementación (para el agente)

1. **Parsear entrada** (flags / JSON). Validar esquema.
2. **Cargar parámetros** desde `params/2025.json` (si existe) o usar defaults.
3. **Validaciones legales**: tipo_contrato != prestación de servicios; fechas coherentes; salario > 0.
4. **Calcular DIAS_SERVICIO** (considerar exclusiones si la política lo requiere).
5. **Calcular SBL_GENERAL** y **SBL_VACACIONES**: salario + promedios variables + auxilio_conectividad (solo si aplica).
6. **Aplicar fórmulas**: cesantías, intereses, prima. (Si FINIQUITO, calcular vacaciones e indemnización con tope 20 SMMLV).
7. **Ejecutar control previo de cumplimiento**: validar todas las reglas del CHECKLIST y generar compliance_report.
8. **Si compliance_status == "NO_GO" y enforce-compliance == true**: abortar y mostrar reporte de cumplimiento.
9. **Generar JSON** con desglose, compliance_report y `normas_aplicadas`.
10. **Renderizar comprobante** (MD → PDF opcional).
11. **Imprimir en consola** resumen y ruta del JSON/PDF.
12. **Registrar log** (audit trail) con versión de parámetros usados, hashes y compliance_report.

Pseudocódigo (compacto):

```python
params = load_params()
input = parse_input()
validate_input(input)

# Calcular hashes para auditoría
input_hash = calculate_hash(input)

dias = days_between(input.fecha_ingreso, input.fecha_corte)
sbl_general = compute_sbl_general(input, params)
sbl_vacaciones = compute_sbl_vacaciones(input, params)
ces = round((sbl_general * dias) / params.DIAS_BASE)
int_ces = round((ces * dias * params.TASA_INT_CESANTIAS) / params.DIAS_BASE)
dias_prima = compute_days_semester(input.fecha_corte)
prima = round((sbl_general * dias_prima) / params.DIAS_BASE)

# Construir resultado preliminar
result = build_json(...)

# Ejecutar control de cumplimiento
compliance_report = control_previo(result, input, params)

# Determinar si se puede continuar
if input.get("enforce-compliance", True) and compliance_report["compliance_status"] == "NO_GO":
    if not input.get("human-override", False):
        print("ERROR: Cumplimiento legal no superado. No se genera liquidación.")
        print(json.dumps(compliance_report, indent=2))
        return
    else:
        # Registrar override
        compliance_report["operator_action"] = {
            "action": "human_override",
            "operator_id": input.get("operator-id"),
            "justification": input.get("override-reason")
        }

# Añadir reporte de cumplimiento al resultado
result["compliance_report"] = compliance_report

# Calcular hash final del resultado
output_hash = calculate_hash(result)
result["meta"]["output_hash"] = output_hash

write_json(result, outpath)
render_pdf(result)  # opcional

# Guardar auditoría
save_audit(input, result, compliance_report)
```

---

# 10) Casos de prueba y ejemplos (esperado)

**Caso**: trabajador que reside en finca — ejemplo tomado de los anexos.

Input: salario 1.500.000, reside_en_lugar_trabajo=true, periodo 2024-11-16 → 2025-11-15 (360 días), auxilio_conectividad=200000

Salida esperada (fragmento):

* `SBL_GENERAL` = 2.000.000 + 200.000 (conectividad si así pactado) = 2.200.000
* `SBL_VACACIONES` = 2.000.000 (sin auxilio ni extras)
* `Cesantias` = 2.200.000
* `Intereses` = 264.000
* `Prima` (semestres) = 1.100.000 por semestre (total 2.200.000 anual) — para periodo muestra 1.100.000 si corresponde.
* `compliance_report` con validaciones pasadas y advertencias sobre auxilio de transporte.

**Edge cases**:

* Contrato prestación de servicios → abortar con compliance_status "NO_GO".
* Salario variable: no hay 12 meses → promediar tiempo real.
* Contrato inicia y termina dentro del mismo semestre → prima proporcional.
* Días de incapacidad o licencia no remunerada → reglas de exclusión si la empresa exige; documentar el criterio.
* Periodo que incluye fecha 2025-07-01 → validar aplicación correcta del recargo dominical del 80%.

---

# 11) Test de regresión a incluir

* Comparar cálculos contra ejemplos conocidos (los del anexo) — assert números exactos.
* Pruebas de validación (contrato, fechas incoherentes).
* Test de redondeo (pesos).
* Test de políticas (auxilio aplicado/excluido).
* Test de validación de plazos de pago.
* Test de validación de tope de indemnización.
* Test de validación de SBL_VACACIONES (excluyendo extras).
* Test de control previo de cumplimiento.

---

# 12) Auditable / trazabilidad legal

* Cada renglón del JSON debe incluir `norma` y `fuente` (puede añadirse URL o referencia corta) para que en auditoría legal se muestre fundamento. Los anexos incluyen la tabla de normas que debes insertar en `params/normas.json`. 
* El JSON debe incluir `params_version`, `input_hash`, `output_hash`, `timestamp` y `generator_version` para garantizar reproducibilidad.
* Todos los cálculos deben registrarse en el directorio `audit/` con timestamp.

---

# 13) Seguridad y cumplimiento

* No persistir datos personales sin consentimiento; en la versión de producción, cifrar archivos con datos sensibles.
* Registrar versión de parámetros (p. ej. `params/version = 2025-10-20`) para reproducibilidad.
* Implementar mecanismo de control previo que valide todas las reglas del CHECKLIST antes de generar la salida final.

---

# 14) Prompt *agentico* (listo para ejecutar en la terminal) — **copia al agente**

Usa este prompt para cargar a un modelo agentico (ej.: Claude / GPT-4o) que debe generar el código en Python (CLI). El prompt es específico, prescriptivo y contiene el objetivo, entradas, outputs, validaciones y formato de salida.

```
ROL: Eres un desarrollador senior de Python experto en nómina y cumplimiento laboral en Colombia. Tu tarea: generar un paquete Python (estructura completa) que implemente la herramienta CLI descrita a continuación.

OBJETIVO: Implementar una CLI 'liquidar' que calcule la Liquidación Periódica (Soporte de Pago) conforme a las reglas legales de Colombia (base 360 días, tasa 12% intereses, auxilio transporte 2025, etc.). La herramienta debe producir un JSON con el desglose, incluir referencias normativas, plazos de pago, y una plantilla Markdown para el comprobante imprimible. Debe implementar un mecanismo de control previo que valide todas las reglas del CHECKLIST antes de generar la salida final. No ejecutes código fuera del entorno; entrega solo el repositorio listo para ejecutar.

ENTRADAS (flags/JSON): --modo, --fecha_ingreso, --fecha_corte, --salario_mensual, --salarios_historicos, --comisiones_promedio_mensual, --horas_extras_promedio_mensual, --bonificaciones_promedio_mensual, --reside_en_lugar_trabajo, --auxilio_transporte, --dias_vacaciones_pendientes, --tipo_contrato, --motivo_terminacion, --salario_pendiente, --enforce-compliance, --compliance-policy, --human-override, --operator-id, --override-reason.

SALIDAS: JSON con campos meta, trabajador, parametros, desglose (SBL_GENERAL, SBL_VACACIONES, cesantias, intereses, prima, vacaciones si aplica), total_liquidacion_periodica, validaciones_y_alertas, normas_aplicadas, compliance_report. Además generar MD comprobante.

REGLAS LEGALES/FORMULAS:
- Cesantías = (SBL_GENERAL * dias) / 360
- Intereses = (Cesantias * dias * 0.12) / 360
- Prima = (SBL_PRIMA * dias_semestre)/360
- Vacaciones = (SBL_VACACIONES * dias_vacaciones)/720
- Auxilio de transporte NO aplica si reside_en_lugar_trabajo == true
- Si tipo_contrato == 'prestación_servicios' → abortar
- SBL_VACACIONES debe excluir horas extras, recargos y auxilio de transporte/conectividad
- Validar plazos de pago: Cesantías (14-Feb), Intereses (31-Ene), Prima (30-Jun, 31-Dic)
- Validar tope de indemnización: 20 SMMLV
- Validar aplicación de recargo dominical 80% solo desde 2025-07-01

PARÁMETROS INICIALES:
SMMLV=1423500; AUXILIO_TRANS=200000; LIMITE_AUXILIO=2*SMMLV; TASA_INT_CESANTIAS=0.12; DIAS_BASE=360; TOPE_INDEMNIZACION_SMMLV=20; FECHA_APLICACION_RECARGO_DOMINICAL="2025-07-01".

ENTREGABLES:
1) Código Python (módulos indicados en la especificación) con tests unitarios y ejemplos en /examples.
2) README con instrucciones de instalación y uso (ejemplos CLI).
3) File params/2025.json y params/normas.json con referencias usadas.
4) Un archivo example_input.json con el caso de la finca (reside_en_lugar_trabajo=true).
5) Script para generar PDF a partir de MD (opcional, documentado).
6) Módulo compliance_checker.py que implemente todas las validaciones del CHECKLIST.
7) Tests unitarios para el módulo de compliance_checker.py.

CRITERIO DE ACEPTACIÓN:
- Ejecutando `python -m liquidator.bin.liquidar --input examples/example_input.json` produce un JSON cuyo `desglose.cesantias` coincide con el cálculo del anexo (ejemplo) y `validaciones_y_alertas` indica que el auxilio de transporte fue excluido por residencia en la finca.
- El compliance_report debe incluir todas las validaciones del CHECKLIST y el estado debe ser "GO".
- Tests unitarios pasan, incluyendo los de compliance_checker.py.

MATERIALES DE REFERENCIA: integrar en output los identificadores normativos que aparecen en los documentos entregados (Art. 249-250 CST, Ley 50/1990 Art.99, Art.306-308 CST, Art.65 CST, Art.64 CST, Art.192 CST, Ley 2466/2025). Usa los ejemplos numéricos dados como base para pruebas.

OBLIGATORIO: Implementa un módulo `compliance_checker.py` que:
- Cargue y aplique íntegramente el CHECKLIST_CUMPLIMIENTO_LEGAL_NOMINA.md (adjunto) como fuente de reglas.
- Ejecute todas las validaciones descritas y devuelva un `compliance_report` (esquema provisto).
- Si `--enforce-compliance` está activo y el `compliance_status == "NO_GO"`, la ejecución debe terminar sin generar el JSON/MD/PDF final y debe devolver sólo el `compliance_report` con evidencia para corrección.
- Soportar `--human-override` con registro explícito (operator_id, justification).
- Guardar en `audit/` los artefactos: input, output (parcial si aborta), report.
- Entregar tests unitarios que cubran cada validación crítica.

Usa CHECKLIST_CUMPLIMIENTO_LEGAL_NOMINA.md como fuente normativa. (ver anexo).
```

---

# 15) Notas finales / recomendaciones para el agente implementador

* Documentar claramente **cómo** el SBL incorpora (o no) el auxilio de transporte; dejar flag explícito para que un auditor pueda verificar la decisión.
* Mantener `params` en archivo separado y versionado.
* Incluir logs con `params_version` y `timestamp` dentro del JSON para reproducibilidad.
* Añadir pruebas legales unitarias: por ejemplo, que la consignación de cesantías tenga una nota de plazo (14-Feb) en output al ser anual.
* Mantener la trazabilidad de `normas_aplicadas` (artículo y texto fuente o URL en `params/normas.json`).
* Implementar el mecanismo de control previo como una barrera obligatoria antes de generar cualquier salida legal.
* Validar específicamente la aplicación del recargo dominical del 80% solo para periodos posteriores a 2025-07-01.
* Asegurar que el SBL_VACACIONES excluya correctamente horas extras, recargos y auxilio de transporte/conectividad.
* Validar que las vacaciones no se incluyan en modo PERIÓDICA, solo en FINIQUITO.
* Implementar validación de plazos de pago para cada prestación según normativa vigente.