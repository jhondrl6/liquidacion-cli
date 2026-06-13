# Addendum al Plan v2.0: Anualización Salarial (SL2630-2024) e Indexación IPC

> **ESTADO:** APROBADO CON REPAROS — ejecución diferida a sesión(es) futura(s).
> Aprobado conceptualmente el 2026-06-09 durante revisión del plan v2.0
> contra la sentencia SL2630-2024 de la Corte Suprema de Justicia.
> **Reparos críticos antes de ejecutar:** corregir Art. 155 CST por Art. 488 CST,
> verificar texto/sala/URL oficial de SL2630-2024, y modelar IPC como índices
> acumulados, no como tasas anuales de inflación.
> **Archivo a impactar al ejecutar:** Planificación/plan_modernizacion_v2.0_2026-06-09.md
> **Tareas que crea:** 1.C-bis, 2.B-bis, 2.X
> **Versión objetivo al incorporar:** v2.0.1 si v2.0 ya se congela; si no, absorber
> en v2.0.0 como corrección de alcance antes del release.

## Decisiones de aprobación (2026-06-09)

- Concepción del addendum: APROBADA CON REPAROS
- Versión objetivo: **v2.0.1** si v2.0 ya se congela; si no, absorber en
  **v2.0.0** como corrección de alcance antes del release.
- Distribución por fase:
  - **Tarea 1.C-bis** (extender schema `Salario`) → Fase 1 ampliada
  - **Tarea 2.B-bis** (SBL del año del segmento) → Fase 2 ampliada
  - **Tarea 2.X** (indexación IPC) → Fase 2 ampliada o Fase 2-bis
- Reparos bloqueantes para ejecución:
  - Reemplazar cualquier cita a **Art. 155 CST** por **Art. 488 CST** cuando se hable
    de prescripción de acciones laborales.
  - Verificar texto literal, sala y URL oficial de **SL2630-2024** antes de tratar su
    `texto_relevante` como cita verificada.
  - Modelar IPC como **índice acumulado mensual/anual**, no como tasa anual de inflación.
- Convención de trabajo: 1 fase por sesión (respetar convención del usuario)
- Próxima sesión sugerida: ejecutar Tarea 1.C-bis (la de menor riesgo, que
  desbloquea las otras dos). Antes de tocar código, validar:
  - `liquidator/core/params_provider.py` ya es year-aware en código vivo
  - `liquidator/contracts/input_model.py` schema actual de `Salario`
  - `legal_docs/` para confirmar si SL2630-2024 ya está citada
  - `Contexto/diagnostico_liquidacion_cli_2026-06-09.md` para ver si el
    diagnóstico original cubre parcialmente las brechas

---

## A. Motivación y brechas detectadas en el plan vigente

| # | Brecha | Impacto | Referencia |
|---|--------|---------|------------|
| 1 | SBL es un único valor (no segmentado por año) | Caso canónico pasa por coincidencia (SBL constante); falla con variabilidad salarial | SL2630-2024 anualización |
| 2 | Salario variable = "promedio últimos 6 meses" | Regla jurisprudencial exige promedio POR AÑO, no del periodo total | SL2630-2024 anualización |
| 3 | Indexación IPC para prestaciones de años anteriores no pagadas oportunamente | Ausencia total: no hay tarea, no hay nota KB, no hay fórmula; además se debe separar prescripción (Art. 488 CST) de indexación | Art. 488 CST, SL2630-2024, DANE IPC |
| 4 | Plan cita "CST art. 253, Ley 50/1990" sin nombrar SL2630-2024 | Debilidad jurisprudencial del plan | Mejora de cita |

Las brechas 1, 2 y 4 comparten la opción B (anualización salarial). La brecha 3 es la opción C (indexación).

## B. Diseño

### B.1 Modelo de salario (anualización)

**Mutuamente excluyentes — el input elige uno:**

- **B.1.a Simple** — `SBL_por_anio: dict[int, Decimal]` cuando el usuario conoce
  el SBL exacto de cada año calendario. Mínimo cambio al schema actual.
- **B.1.b Completo** — `historial_salarial: list[MesValor]` con la serie mensual
  del salario. El motor calcula el promedio del año del segmento. Cubre salario
  variable correctamente. **Recomendado.**

Ambas formas son compatibles entre sí (motor intenta B.1.b primero, fallback
a B.1.a, fallback a `SBL` único actual).

### B.2 Cálculo de prestaciones por año del segmento

`ParamsProvider.for_range(desde, hasta)` debe quedar como contrato year-aware
(idealmente retorna `{año: params}` normativos; si el código vivo aún no lo
tiene, ejecutar Tarea 1.E antes de esta). La opción B extiende esto a
`{año: SBL_del_año}` salarial. La calculadora recibe por segmento:

```python
class SegmentoCalculo:
    anio: int
    desde: date
    hasta: date
    sbl: Decimal                  # SBL del año (no del periodo total)
    params: ParamsProvider        # params normativos del año
    dias: int                     # días del segmento en este año
```

`calculate_cesantias(sbl, dias, params)` opera SIN CAMBIOS — la anualización
se logra pasando el SBL correcto por segmento. El motor itera segmentos y
suma.

### B.3 Indexación IPC (opción C)

Nuevo módulo `liquidator/calculators/indexacion.py` + fuente de datos DANE en
`params/ipc_dane_mensual.json` (preferible) o `params/ipc_dane_anual.json` (fallback).
La fuente debe almacenar **índices acumulados de precios**, no tasas anuales de inflación.
Si se usa inflación anual DANE, el loader debe convertirla a índice acumulado antes de
calcular.

```python
class IPCIndexador:
    def __init__(self, ipc_index: dict[str, Decimal], base_year: int = 2010):
        # ipc_index usa claves "YYYY" o "YYYY-MM" con valores de índice acumulado.
        self.data = {k: Decimal(str(v)) for k, v in ipc_index.items()}

    def indice_para(self, fecha: date | str) -> Decimal:
        # Preferir índice mensual. Si solo hay anual, usar diciembre o promedio anual,
        # según la regla documentada en params/ipc_dane_*.json.
        ...

    def indexar(self, vh: Decimal, fecha_origen: date | str, fecha_referencia: date | str) -> Decimal:
        """VA = VH × (ÍndiceIPC_referencia / ÍndiceIPC_origen).
        Aplica a prestaciones no pagadas oportunamente. No usar inflación anual
        directa como si fuera índice.
        """
        ipc_origen = self.indice_para(fecha_origen)
        ipc_ref = self.indice_para(fecha_referencia)
        return (vh * ipc_ref / ipc_origen).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
```

Activación: cuando el input declara `periodos_no_pagados: [{concepto, valor_historico,
fecha_causacion, fecha_exigibilidad, fecha_referencia_indexacion}]`, el motor valida
prescripción según Art. 488 CST y añade al desglose un renglón `<concepto>_indexado`
con la VA calculada, la cita legal y la advertencia si requiere verificación jurídica.

## C. Tareas

### Tarea 1.C-bis — Extender `Salario` con historial/B.1

**Archivos:** `liquidator/contracts/input_model.py`,
`Contexto/KB_LLM/04_schema_entrada.md` (actualizar),
`examples/inputs/caso_canonico_periodico_206d.json` (actualizar).

**Cambios al schema:**

```python
class MesValor(BaseModel):
    año: int
    mes: int = Field(ge=1, le=12)
    valor: Decimal = Field(gt=0)

class Salario(BaseModel):
    # Existentes (compatibilidad)
    SBL: Decimal = Field(gt=0)
    auxilio_transporte: bool = False
    variable: bool = False
    dias_trabajados: int | None = None

    # NUEVOS (opcionales, retrocompatibles)
    sbl_por_anio: dict[int, Decimal] | None = None
    historial_salarial: list[MesValor] | None = None

    @model_validator(mode="after")
    def _consistencia(self):
        if self.variable and not self.historial_salarial and not self.sbl_por_anio:
            raise ValueError("Salario variable requiere historial_salarial o sbl_por_anio")
        return self
```

**DoD:** Tests verdes; input canónico sigue pasando (sin campos nuevos
rellenos = comportamiento idéntico al actual).

### Tarea 2.B-bis — Calcular prestaciones con SBL del año del segmento

**Archivos:** `liquidator/calculators/prestaciones.py`,
`liquidator/core/engine.py`, `liquidator/core/salario_resolver.py` (nuevo).

**Lógica:**

```python
# salario_resolver.py
class SalarioResolver:
    def __init__(self, salario: Salario, ipc_indexador: IPCIndexador | None = None):
        self.salario = salario

    def sbl_para_segmento(self, segmento: SegmentoCalculo) -> Decimal:
        # Prioridad 1: historial mensual → promedio del año del segmento
        if self.salario.historial_salarial:
            meses_del_anio = [m for m in self.salario.historial_salarial
                               if m.año == segmento.anio]
            if meses_del_anio:
                return sum(m.valor for m in meses_del_anio) / len(meses_del_anio)
        # Prioridad 2: SBL explícito por año
        if self.salario.sbl_por_anio and segmento.anio in self.salario.sbl_por_anio:
            return self.salario.sbl_por_anio[segmento.anio]
        # Prioridad 3: SBL único (compatibilidad)
        return self.salario.SBL
```

**DoD:** Caso canónico verde (con `historial_salarial` rellenado, SBL
promedio por año = 2.200.000 → resultado idéntico al actual); caso nuevo
"SBL variable" produce SBL distinto por segmento.

### Tarea 2.X — Indexación IPC para prestaciones no pagadas oportunamente

**Archivos:** `liquidator/calculators/indexacion.py` (nuevo),
`liquidator/legal/normas_repository.py` (agregar SL2630-2024 y CST_488_PRESCRIPCION),
`params/normas.json` (entradas nuevas), `params/ipc_dane_mensual.json` (nuevo,
fuente DANE; fallback `params/ipc_dane_anual.json`), `params/checklist.json` (regla
`V_INDEXACION_IPC`), `Contexto/KB_LLM/01_reglas_calculo.md` (nota sobre prescripción
e indexación), `liquidator/tests/test_calculators/test_indexacion.py` (nuevo),
`liquidator/tests/test_golden/test_prescripcion_indexada.py` (nuevo).

**Entradas en `params/normas.json`:**
```json
{
  "id": "SL2630_2024",
  "nombre": "Sentencia SL2630-2024 Corte Suprema de Justicia",
  "descripcion": "Criterio jurisprudencial sobre liquidación anual de prestaciones adeudadas e indexación por pérdida de poder adquisitivo.",
  "texto_relevante": "RESUMEN NO LITERAL — pendiente de verificación verbatim con fuente oficial: las prestaciones adeudadas de años anteriores deben liquidarse año por año con el salario correspondiente a cada año y luego indexarse a valor presente.",
  "estado_verificacion": "PENDIENTE_VERBATIM",
  "sala": "Pendiente de verificación oficial; fuentes secundarias indican Sala de Descongestión Laboral N.º 1.",
  "url": "https://siugj.ramajudicial.gov.co/",
  "vigencia": "2024"
},
{
  "id": "CST_488_PRESCRIPCION",
  "nombre": "Código Sustantivo del Trabajo Art. 488",
  "descripcion": "Regla general de prescripción de acciones laborales: tres años desde que la obligación se hace exigible, salvo prescripciones especiales.",
  "texto_relevante": "RESUMEN NO LITERAL — verificar texto oficial en SUIN/CST: las acciones correspondientes a los derechos regulados en el CST prescriben en tres (3) años; en relación de trabajo, el término se cuenta desde que la obligación se hace exigible.",
  "estado_verificacion": "PENDIENTE_VERBATIM",
  "url": "https://www.suin-juriscol.gov.co/",
  "vigencia": "permanente"
}
```

**Regla en `params/checklist.json`:**
```json
{
  "id": "V_INDEXACION_IPC",
  "description": "Indexación IPC para prestaciones no pagadas oportunamente: VA = VH × (ÍndiceIPC_referencia / ÍndiceIPC_causacion). Validar prescripción según Art. 488 CST cuando corresponda.",
  "severity": "MEDIUM",
  "blocking": false,
  "rule_ref": "SL2630-2024; Art. 488 CST (prescripción); DANE IPC",
  "formula": "VA = VH × (ÍndiceIPC_referencia / ÍndiceIPC_causacion)",
  "nota": "No usar tasas anuales de inflación como si fueran índices acumulados."
}
```

**DoD:**
- `IPCIndexador.indexar(Decimal("1000000"), "2020-02-14", "2025-06-09")`
  retorna valor actualizado coherente con datos DANE reales e índices acumulados
- Test golden verde con caso de prescripción/indexación: prestación 2020 ($1M)
  → VA 2025 con IPC acumulado real
- `Contexto/KB_LLM/01_reglas_calculo.md` incluye sección "Indexación por IPC"
  con cita SL2630-2024 + Art. 488 CST + fórmula
- Compliance Engine reconoce `periodos_no_pagados` en input y aplica la regla
  sin bloquear, advirtiendo si requiere verificación jurídica

## D. DoD agregado del addendum

- [ ] Schema `Salario` extendido con `sbl_por_anio` y `historial_salarial`
      (retrocompatible)
- [ ] `SalarioResolver` selecciona SBL correcto por año del segmento
- [ ] Caso canónico sigue verde (con o sin campos nuevos)
- [ ] Caso nuevo "SBL cambia a mitad de periodo" produce cálculos distintos
      por año
- [ ] `IPCIndexador` implementado con tests contra **índices acumulados** DANE reales
- [ ] Regla `V_INDEXACION_IPC` en checklist (severity MEDIUM, no bloqueante)
- [ ] SL2630-2024 y Art. 488 CST citados en `params/normas.json` y `KB_LLM/01_reglas_calculo.md`
- [ ] No quedan citas a Art. 155 CST como sustento de prescripción o indexación
- [ ] Test golden de prescripción/indexación verde
- [ ] Suite al 100%

## E. Estimación de esfuerzo

| Tarea | Esfuerzo | Dependencias |
|-------|----------|--------------|
| 1.C-bis | Bajo (1 sesión) | Ninguna — schema retrocompatible |
| 2.B-bis | Medio (1-2 sesiones) | 1.C-bis; requiere validación cruzada del caso canónico contra cálculo manual |
| 2.X | Alto (3-4 sesiones) | 2.B-bis (comparte motor); requiere descarga, validación y conversión de datos DANE a índices acumulados; cita legal verificada |
| **Total** | **4-6 sesiones** | Acotar a 1 fase por sesión (convención del usuario) |

## F. Riesgos

- **R1:** Datos DANE pueden no estar en formato JSON, requieren parsing de
  CSV/XLS. Mitigación: script `scripts/build_ipc_index.py` en Tarea 2.X que
  convierta inflación anual/mensual a índice acumulado.
- **R2:** `SalarioResolver` cambia contrato con calculadoras existentes.
  Mitigación: el resultado del caso canónico NO debe cambiar (validación
  de regresión obligatoria).
- **R3:** SL2630-2024 puede no estar disponible en URL pública
  (sentencias CSJ a veces solo en relatoría). Mitigación: si no se
  encuentra URL oficial, citar con texto completo verificado en
  `params/normas.json` y documentar fuente en KB; mientras tanto marcar
  `estado_verificacion: PENDIENTE_VERBATIM`.
- **R4:** La cita de prescripción NO debe usar Art. 155 CST. Mitigación:
  usar Art. 488 CST y verificar texto literal en SUIN/CST antes de cerrar
  Tarea 2.X.
- **R5:** Riesgo de confundir inflación anual con índice IPC. Mitigación:
  tests unitarios que demuestren que `IPCIndexador` usa índices acumulados;
  rechazar datos DANE si solo contienen tasas anuales sin conversión.

## G. Decisión recomendada

1. **Aprobar el addendum con reparos** e incorporarlo al plan v2.0 como
   corrección de alcance. Si v2.0 ya se congela, usar **v2.0.1**; si no,
   absorber en **v2.0.0** antes del release.
2. **Orden sugerido:** Tarea 1.E (`ParamsProvider` year-aware) → Tarea 1.C-bis →
   Tarea 2.B-bis → Tarea 2.X.
3. **Costo de NO hacerlo:** las 3 brechas quedan abiertas. El sistema
   puede calcular el caso canónico simple pero NO casos reales con variabilidad
   salarial ni casos con prestaciones de años anteriores. La cobertura
   legal del sistema queda incompleta y aumenta el riesgo de liquidaciones
   jurídicamente discutibles.

## H. Referencias legales (verificar verbatim antes de cierre)

- **SL2630-2024** Corte Suprema de Justicia — anualización de prestaciones
  adeudadas e indexación por pérdida de poder adquisitivo. Verificar sala,
  URL oficial y texto literal en relatoría/SIUGJ antes de marcarla como
  verificada.
- **Art. 488 CST** — prescripción general de acciones laborales (3 años,
  contados desde que la obligación se hace exigible, salvo prescripciones
  especiales). Verificar texto literal en SUIN/CST.
- **CST art. 253** — definición de cesantías (ya en plan).
- **Ley 50/1990 art. 99** — régimen de cesantías e intereses (ya en plan).
- **Art. 65 CST** — pago inmediato en terminación/finiquito, si se requiere
  para plazos de pago.

## I. Compatibilidad hacia atrás

- `Salario` con solo `SBL` (sin campos nuevos) = comportamiento actual
  intacto para el caso canónico. **No es breaking para inputs simples.**
- `Salario` con `sbl_por_anio` o `historial_salarial` = nuevo
  comportamiento opt-in para salario variable y anualización.
- `periodos_no_pagados` = nuevo comportamiento opt-in para indexación IPC.
- Documentos v2.0 existentes siguen siendo válidos, pero deben actualizarse
  las reglas legales: Art. 155 CST queda descartado para prescripción.

Por lo tanto, este addendum puede entrar como **v2.0.1** si v2.0 ya se
congela, o absorberse en **v2.0.0** si el release aún no se cierra. En ambos
casos, no debe avanzar con Art. 155 CST ni con IPC como tasa anual directa.

---

## J. Hand-off a próxima sesión

**Para el operador (Jhond) o agente que ejecute la próxima fase:**

1. **Cargar antes de empezar:** `skill_view(name='iah-cli-execution-conventions')`
   (NO — ese es para iah-cli; este proyecto es liquidacion_cli. La doctrina
   "validar contra código vivo" sí aplica).
2. **Validar primero (sin tocar código):**
   - Leer `liquidator/contracts/input_model.py` si existe; si no, ubicar el
     schema actual de `Salario` en contratos/input/parsers vivos
   - Leer `liquidator/core/params_provider.py` si existe; si no, registrar Tarea 1.E como pendiente
   - `ls legal_docs/` y buscar "SL2630", "IPC", "Art. 488", "prescripción"
   - `grep -r "Art. 155\\|SL2630\\|IPC\\|indexación" Contexto/ params/ legal_docs/`
     para detectar citas heredadas incorrectas
3. **Orden de ejecución recomendado:** si `ParamsProvider` no existe o no es
   year-aware, ejecutar primero Tarea 1.E del plan original; luego Tarea 1.C-bis.
4. **Ejecutar Tarea 1.C-bis** (primera del addendum, menor riesgo):
   - Modificar schema con campos opcionales
   - Agregar tests
   - Validar que caso canónico SIN campos nuevos sigue verde
5. **Actualizar al cerrar:** `Contexto/KB_LLM/09_caso_canonico_usuario.md` con
   resultado de la sesión; sincronizar `REGISTRY.md`/checklist si existen.
6. **Si el operador decide NO ejecutar este addendum ahora:** el plan v2.0
   sigue vigente y el sistema es funcional para casos con SBL constante. Las
   brechas quedan registradas en este documento como referencia futura.

*Addendum aprobado el 2026-06-09 a partir del análisis del plan v2.0 contra SL2630-2024.*
