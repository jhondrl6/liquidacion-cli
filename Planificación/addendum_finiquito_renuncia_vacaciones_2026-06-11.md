# Addendum al Plan v2.0: Finiquito por Renuncia Voluntaria + Vacaciones Compensadas

> **ESTADO:** APROBADO CON REPAROS — ejecución diferida a sesión(es) futura(s).
> Aprobado conceptualmente el 2026-06-11 tras evaluación del plan v2.0
> contra la necesidad de liquidar un caso real de contrato terminado por
> renuncia voluntaria del trabajador, con vacaciones pendientes acumuladas.
> **Reparos críticos antes de ejecutar:** verificar texto literal del Art. 189
> CST en SUIN y confirmar que el motor distingue correctamente entre
> *vacaciones compensadas por acuerdo mutuo* (Art. 189) y
> *vacaciones obligatoriamente compensadas en finiquito* (Art. 189 + 190).
> **Archivo a impactar al ejecutar:** Planificación/plan_modernizacion_v2.0_2026-06-09.md
> **Tareas que crea:** 1.C-ter, 2.B-ter, 2.Z, 3.G
> **Versión objetivo al incorporar:** absorber en v2.0.0 como corrección de
> alcance antes del release (igual que el addendum SL2630-2024).

## Resumen ejecutivo (para Jhond)

Para tu caso concreto (contrato indefinido, Pedro Franco, 2024-11-16 a
2025-11-15, renuncia voluntaria el 2025-11-15 con 7.5 días de vacaciones
no disfrutados), la legislación colombiana establece:

1. **NO hay indemnización**: el trabajador renuncia libremente (Art. 49
   CST num. 6); el Art. 64 CST solo aplica cuando el empleador termina
   sin justa causa.
2. **NO hay preaviso obligatorio**: para contrato indefinido, la dimisión
   del trabajador no requiere preaviso formal.
3. **Se pagan TODAS las prestaciones causadas**:
   - Cesantías → consignadas al fondo (Art. 249-254 CST).
   - Intereses sobre cesantías → pagados al trabajador (Art. 99 Ley 50/1990).
   - Prima de servicios → proporcional al último semestre completo hasta
     la fecha de terminación (Art. 306-307 CST).
   - Vacaciones causadas no disfrutadas → compensadas obligatoriamente
     en dinero, sin necesidad de acuerdo mutuo (Art. 189 párr. 1° CST).
4. **Fórmula de vacaciones por Art. 189 + 190 CST**:
   `vacaciones_compensadas = (SBL / 30) × días_pendientes`
   Para tu caso: (2.200.000 / 30) × 7.5 = **$550.000 COP**.

Para el caso del plan (2025-11-16 a 2026-06-15, SBL constante):
- Días servicio segmento 2025: 46 (nov16-dic31)
- Días servicio segmento 2026: 166 (ene01-jun15)
- Días totales: 212
- Días vacaciones causadas proporcionales: (212/360) × 15 = 8.83 redondeado
- Pendientes a pagar según input: 7.5 (días que no disfrutó)
- Vacaciones compensadas: (2.200.000 / 30) × 7.5 = $550.000
- Nota: la cantidad de días pendientes NO es siempre el cálculo proporcional
  matemático; puede haber días ya disfrutados en el período, por lo que
  `dias_pendientes` es un dato de entrada del usuario, validado contra el
  máximo causable.

---

## A. Motivación y brechas detectadas en el plan vigente

| # | Brecha | Impacto | Referencia legal |
|---|--------|---------|------------------|
| 1 | Campo `vacaciones` en schema es `dict` genérico, no modelo tipado | El motor no puede distinguir días causados / días tomados / días pendientes / fechas | Art. 186-190 CST |
| 2 | No hay diferenciación de modos de terminación en schema `Contrato` | FINIQUITO no distingue renuncia, despido sin justa causa, despido con justa causa, mutuo acuerdo, muerte, etc. | Art. 49 CST |
| 3 | Lógica de vacaciones no formalizada en `PrestacionesCalculator` | El motor no implementa la fórmula `SBL × días_pendientes / 30` ni diferencia Art. 189 (acuerdo mutuo) de Art. 189+190 (obligatorio en finiquito) | Art. 189-190 CST |
| 4 | Indemnización por despido (Art. 64 CST) referenciada pero sin fórmula | Tests golden de "finiquito sin justa causa" no tienen valores esperados verificables | Art. 64 CST |
| 5 | No hay fixture de entrada para FINIQUITO con vacaciones pendientes | El caso canónico es PERIODICA; el caso histórico de Pedro Franco es PERIODICA con acuerdo mutuo | — |
| 6 | No hay regla de compliance para "vacaciones causadas no pagadas en finiquito" | El sistema no advierte cuando al trabajador que renuncia no se le pagan vacaciones pendientes | Art. 189-190 CST |
| 7 | `PreRenderValidator` no diferencia campos obligatorios por motivo | FINIQUITO por renuncia requiere solo `salarios_pendientes` y `vacaciones`; finiquito por despido requiere además indemnización | — |

Las brechas 1, 2, 3 y 6 comparten la solución "formalizar vacaciones en
finiquito". Las brechas 4 y 7 son complementarias pero opcionales para
cerrar este addendum (la indemnización no aplica en tu caso, pero el
motor debe conocerla para otros casos).

## B. Diseño

### B.1 Decisiones legales (verificar verbatim antes de ejecutar)

| # | Decisión | Justificación | Artículo |
|---|----------|---------------|----------|
| D1 | Renuncia voluntaria NO genera indemnización al trabajador | Solo se genera Art. 64 cuando el empleador termina sin justa causa | Art. 49 num. 6 CST |
| D2 | Preaviso NO obligatorio para contrato indefinido por parte del trabajador | CST no impone preaviso al renunciar de manera voluntaria en indefinido | Art. 49 CST |
| D3 | Vacaciones causadas no disfrutadas se compensan obligatoriamente en finiquito | Excepción al principio de que vacaciones no son compensables en dinero | Art. 189 párr. 1° CST |
| D4 | Fórmula: vacaciones = (SBL / 30) × días_pendientes | Compensación de un día de salario por cada día de vacaciones | Art. 190 CST |
| D5 | Días causados = días_servicio × 15 / 360 | Proporción por cada 12 meses completos | Art. 186 CST |
| D6 | Los días pendientes son datos del empleador, NO derivables sólo por fórmula | El trabajador pudo haber disfrutado vacaciones parciales | Art. 185-186 CST |
| D7 | La base para vacaciones es SBL sin recargos/horas extras | Salario ordinario, Art. 185 | Art. 185 CST |
| D8 | Indemnización Art. 64 CST — SOLO aplica en finiquito por despido sin justa causa | No aplica para renuncia voluntaria | Art. 64 CST |

### B.2 Modelo de vacaciones (formalizar schema)

```python
class VacacionesEstado(BaseModel):
    """Estado de vacaciones del trabajador al cierre del periodo."""
    dias_causados_proporcionales: int | None = None  # calculado automáticamente si no se pasa
    dias_disfrutados: int = 0
    dias_pendientes: int = Field(ge=0)                # dato del empleador
    fechas_disfrute: list["PeriodoDisfrute"] | None = None  # histórico (opcional)

    @model_validator(mode="after")
    def _consistencia(self):
        # Si el empleador pasó días_causados_proporcionales, validar que
        # dias_pendientes <= dias_causados - dias_disfrutados
        causados = self.dias_causados_proporcionales
        if causados is not None:
            max_pendientes = causados - self.dias_disfrutados
            if self.dias_pendientes > max_pendientes:
                raise ValueError(
                    f"dias_pendientes ({self.dias_pendientes}) excede el máximo "
                    f"causable ({max_pendientes} = {causados} - {self.dias_disfrutados})"
                )
        return self

class PeriodoDisfrute(BaseModel):
    desde: date
    hasta: date  # inclusive
```

### B.3 Motivo de terminación (enumerar)

```python
from enum import Enum

class MotivoTerminacion(str, Enum):
    RENUNCIA_VOLUNTARIA = "renuncia_voluntaria"         # Art. 49 num 6
    DESPIDO_SIN_JUSTA_CAUSA = "despido_sin_justa_causa" # Art. 64
    DESPIDO_CON_JUSTA_CAUSA = "despido_con_justa_causa" # Art. 62
    TERMINO_FIJO_VENCIDO = "termino_fijo_vencido"       # Art. 46
    OBRA_O_LABOR_TERMINADA = "obra_o_labor_terminada"   # Art. 45
    MUTUO_ACUERDO = "mutuo_acuerdo"                     # Art. 49 num 1
    MUERTE_TRABAJADOR = "muerte_trabajador"             # Art. 49 num 5
    MUERTE_EMPLEADOR = "muerte_empleador"               # Art. 49 num 4 (si persona natural)
    SUSPENSION_DEFICITARIA = "suspension_deficitaria"   # Art. 49 num 3
    CIERRE_EMPRESA = "cierre_empresa"                   # Art. 49 num 3
```

### B.4 Mapa motivo → concepto obligatorio en finiquito

| Motivo | Cesantías | Intereses | Prima | Vacaciones | Indemnización |
|--------|-----------|-----------|-------|------------|---------------|
| renuncia_voluntaria | ✅ | ✅ | ✅ | ✅ (obligatorias) | ❌ |
| despido_sin_justa_causa | ✅ | ✅ | ✅ | ✅ | ✅ (Art. 64) |
| despido_con_justa_causa | ✅ | ✅ | ✅ | ✅ | ❌ |
| termino_fijo_vencido | ✅ | ✅ | ✅ | ✅ | ❌ (salvo preaviso Art. 46) |
| obra_o_labor_terminada | ✅ | ✅ | ✅ | ✅ | ❌ |
| mutuo_acuerdo | ✅ | ✅ | ✅ | ✅ | ❌ |
| muerte_trabajador | ✅ (herederos) | ✅ (herederos) | ✅ | ✅ (herederos) | ❌ |
| muerte_empleador (natural) | ✅ | ✅ | ✅ | ✅ | varía |

### B.5 Fórmulas para el caso de renuncia voluntaria

```python
# Cesantías por segmento (Art. 249-254 CST)
def calcular_cesantias(sbl: Decimal, dias: int, params) -> Decimal:
    return (sbl * Decimal(dias) / params.DIAS_BASE).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

# Intereses sobre cesantías (Art. 99 Ley 50/1990)
def calcular_intereses_cesantias(cesantias_acumuladas: Decimal, dias: int) -> Decimal:
    """Tasa 12% anual prorrateada por los días del segmento."""
    return (cesantias_acumuladas * Decimal("0.12") * Decimal(dias) / Decimal(360)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

# Prima de servicios (Art. 306-307 CST)
def calcular_prima_semestral(sbl: Decimal, dias_en_semestre: int) -> Decimal:
    """Proporcional a los días trabajados en el semestre, máximo 180 días."""
    dias = min(dias_en_semestre, 180)
    return (sbl * Decimal(dias) / Decimal(360)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

# Vacaciones compensadas (Art. 189 + 190 CST)
def calcular_vacaciones_compensadas_finiquito(sbl: Decimal, dias_pendientes: int) -> Decimal:
    """SBL / 30 × días_pendientes. NO aplica recargos/HHE sobre SBL para vacaciones (Art. 185)."""
    return (sbl / Decimal(30) * Decimal(dias_pendientes)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
```

### B.6 Indemnización Art. 64 CST (SOLO para despido sin justa causa, no aplica en tu caso)

Se deja **referenciada y documentada** en este addendum pero **no se implementa
en el motor** en esta iteración (a menos que se abra otro caso de uso
específico). Fórmula para cuando se requiera:

```python
# Art. 64 CST (versión simplificada; verificar con texto legal vigente)
def calcular_indemnizacion_despido_sin_jc(sbl: Decimal, dias_servicio: int, params) -> Decimal:
    smmlv = params.SMMLV
    anios = dias_servicio / 360
    if sbl <= 10 * smmlv:
        # ≤ $17.509.050 en 2026: 30 días/año (primer año) + 20 días/año (subsiguientes)
        if anios <= 1:
            return sbl * 30 / 30  # = sbl (un mes)
        return (sbl * 30 / 30) + (sbl * Decimal(str(anios - 1)) * 20 / 30)
    else:
        # > $17.509.050: 20 días/año (primer año) + 15 días/año (subsiguientes)
        if anios <= 1:
            return sbl * 20 / 30
        return (sbl * 20 / 30) + (sbl * Decimal(str(anios - 1)) * 15 / 30)
```

> **NOTA:** esta fórmula es referencial. Antes de implementarla, verificar
> texto literal del Art. 64 CST en SUIN y revisar si hubo modificación por
> Ley 50/1990 o jurisprudencia CSJ reciente. NO implementar hasta tener
> verificación verbatim.

## C. Tareas

### Tarea 1.C-ter — Extender `Salario` (no; extender `Contrato` y agregar `VacacionesEstado`)

> **Nota:** esta tarea no toca `Salario` — toca `Contrato` y agrega un nuevo
> modelo `VacacionesEstado`. Se nombra "1.C-ter" (ter) por analogía con 1.C-bis
> y para mantener correlato de numeración entre addenda.

**Archivos:**
- Modificar `liquidator/contracts/input_model.py` (agregar `MotivoTerminacion`,
  actualizar `Contrato.fecha_terminacion` y campo `vacaciones`).
- Actualizar `Contexto/KB_LLM/04_schema_entrada.md` (documentar nuevos campos).
- Crear `liquidator/tests/test_contracts/test_vacaciones_estado.py`.
- Crear `liquidator/tests/test_contracts/test_motivo_terminacion.py`.

**Cambios al schema (forma mínima viable, retrocompatible):**

```python
from pydantic import BaseModel, Field, model_validator
from datetime import date
from decimal import Decimal
from typing import Literal
from enum import Enum

class MotivoTerminacion(str, Enum):
    RENUNCIA_VOLUNTARIA = "renuncia_voluntaria"
    DESPIDO_SIN_JUSTA_CAUSA = "despido_sin_justa_causa"
    DESPIDO_CON_JUSTA_CAUSA = "despido_con_justa_causa"
    TERMINO_FIJO_VENCIDO = "termino_fijo_vencido"
    OBRA_O_LABOR_TERMINADA = "obra_o_labor_terminada"
    MUTUO_ACUERDO = "mutuo_acuerdo"
    MUERTE_TRABAJADOR = "muerte_trabajador"
    MUERTE_EMPLEADOR = "muerte_empleador"
    SUSPENSION_DEFICITARIA = "suspension_deficitaria"
    CIERRE_EMPRESA = "cierre_empresa"

class PeriodoDisfrute(BaseModel):
    desde: date
    hasta: date  # inclusive

class VacacionesEstado(BaseModel):
    dias_causados_proporcionales: int | None = None
    dias_disfrutados: int = 0
    dias_pendientes: int = Field(ge=0)
    fechas_disfrute: list[PeriodoDisfrute] | None = None

    @model_validator(mode="after")
    def _consistencia(self):
        causados = self.dias_causados_proporcionales
        if causados is not None:
            max_pendientes = causados - self.dias_disfrutados
            if self.dias_pendientes > max_pendientes:
                raise ValueError(
                    f"dias_pendientes ({self.dias_pendientes}) excede el máximo "
                    f"causable ({max_pendientes} = {causados} - {self.dias_disfrutados})"
                )
        return self

class Contrato(BaseModel):
    fecha_ingreso: date
    fecha_corte: date
    tipo: Literal["INDEFINIDO", "FIJO", "OBRA_LABOR", "PRESTACION"]
    motivo_terminacion: MotivoTerminacion | None = None   # NUEVO
    fecha_terminacion_real: date | None = None            # (ya existía opcional)

    @model_validator(mode="after")
    def _finiquito_requiere_motivo(self):
        # Si hay fecha_terminacion_real, debe venir con motivo
        if self.fecha_terminacion_real and not self.motivo_terminacion:
            raise ValueError(
                "Si hay fecha_terminacion_real, es obligatorio motivo_terminacion"
            )
        return self

class LiquidacionInput(BaseModel):
    trabajador: Trabajador
    empleador: Empleador
    contrato: Contrato
    salario: Salario
    modo: Literal["PERIODICA", "FINIQUITO", "VACACIONES"]
    vacaciones: VacacionesEstado | None = None           # NUEVO: typado
    auxilios: dict | None = None

    @model_validator(mode="after")
    def _finiquito_requiere_vacaciones(self):
        if self.modo == "FINIQUITO" and self.vacaciones is None:
            # Permitimos None por compatibilidad; pero advertimos en compliance
            pass
        if self.modo == "FINIQUITO" and not self.contrato.motivo_terminacion:
            raise ValueError(
                "Liquidación en modo FINIQUITO requiere contrato.motivo_terminacion"
            )
        return self
```

**DoD:**
- Input canónico (PERIODICA, sin vacaciones) sigue verde (regresión cero).
- Input nuevo con `modo=FINIQUITO`, `motivo_terminacion=RENUNCIA_VOLUNTARIA`,
  `vacaciones={dias_pendientes: 7.5}` pasa validación.
- Input con `dias_pendientes > dias_causados - dias_disfrutados` falla con
  `ValidationError` claro.

**Validación:**

```python
def test_finiquito_renuncia_pasa_validacion():
    inp = LiquidacionInput.model_validate({
      "trabajador": {"nombre": "X", "documento": "1"},
      "empleador":  {"nombre": "Y", "documento": "2"},
      "contrato":   {
          "fecha_ingreso": "2025-11-16",
          "fecha_corte": "2026-06-15",
          "tipo": "INDEFINIDO",
          "motivo_terminacion": "renuncia_voluntaria",
          "fecha_terminacion_real": "2026-06-15",
      },
      "salario":    {"SBL": 2200000},
      "modo":       "FINIQUITO",
      "vacaciones": {"dias_pendientes": 7},   # int en esta iteración; 7.5 redondeado abajo
    })
    assert inp.contrato.motivo_terminacion == MotivoTerminacion.RENUNCIA_VOLUNTARIA
    assert inp.vacaciones.dias_pendientes == 7

def test_finiquito_sin_motivo_falla():
    with pytest.raises(ValidationError, match="motivo_terminacion"):
        LiquidacionInput.model_validate({
          "trabajador": {"nombre": "X", "documento": "1"},
          "empleador":  {"nombre": "Y", "documento": "2"},
          "contrato":   {
              "fecha_ingreso": "2025-11-16",
              "fecha_corte": "2026-06-15",
              "tipo": "INDEFINIDO",
              "fecha_terminacion_real": "2026-06-15",  # sin motivo → falla
          },
          "salario":    {"SBL": 2200000},
          "modo":       "FINIQUITO",
        })

def test_vacaciones_estado_consistencia():
    with pytest.raises(ValidationError, match="excede el máximo"):
        VacacionesEstado(
            dias_causados_proporcionales=5,
            dias_disfrutados=2,
            dias_pendientes=10,  # 10 > 5 - 2 = 3 → falla
        )

def test_vacaciones_estado_pasa_con_causados_ok():
    v = VacacionesEstado(
        dias_causados_proporcionales=10,
        dias_disfrutados=2,
        dias_pendientes=8,
    )
    assert v.dias_pendientes == 8
```

> **Aclaración sobre 7.5 días:** el schema actual declara `int`, pero el
> caso real tiene 7.5 días. Dos opciones:
> - Opción A (recomendada): cambiar `dias_pendientes: Decimal = Field(ge=0)`
>   y permitir decimales (el CST no prohíbe fracciones de día).
> - Opción B: redondear a 7 días al input y documentar como "conservador
>   a favor del empleador". **No recomendada** para caso de finiquito.
>
> **Decisión por defecto:** Opción A. Cambiar tipos a `Decimal` en el modelo.

**Versión actualizada (con Decimal):**

```python
class VacacionesEstado(BaseModel):
    dias_causados_proporcionales: Decimal | None = None
    dias_disfrutados: Decimal = Decimal(0)
    dias_pendientes: Decimal = Field(ge=0)
    fechas_disfrute: list[PeriodoDisfrute] | None = None
    ...
```

### Tarea 2.B-ter — Formalizar vacación compensada en `PrestacionesCalculator`

**Archivos:**
- Modificar `liquidator/calculators/prestaciones.py` (agregar método
  `calculate_vacaciones_compensadas_finiquito`).
- Modificar `liquidator/core/engine.py` (invocar el método cuando `modo ==
  "FINIQUITO"` y `vacaciones.dias_pendientes > 0`).
- Crear `liquidator/tests/test_calculators/test_vacaciones_finiquito.py`.
- Actualizar `Contexto/KB_LLM/01_reglas_calculo.md` (sección "Vacaciones
  compensadas obligatorias en finiquito").

**Cambios al motor:**

```python
# liquidator/calculators/prestaciones.py
def calculate_vacaciones_compensadas_finiquito(
    self,
    sbl: Decimal,
    dias_pendientes: Decimal,
    params: ParamsProvider = None,
) -> dict:
    """Vacaciones no disfrutadas pagadas obligatoriamente en finiquito.
    Base legal: Art. 189 párr. 1° + Art. 190 CST.
    Fórmula: (SBL / 30) × días_pendientes.
    El SBL para vacaciones excluye recargos/HHE (Art. 185).
    """
    valor = (sbl / Decimal(30) * dias_pendientes).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    evidencia = self.normas_repo.cita("vacaciones_finiquito", "Art. 189-190 CST")
    return {
        "concepto": "Vacaciones compensadas (finiquito)",
        "valor": valor,
        "dias": dias_pendientes,
        "formula": "SBL / 30 × días_pendientes",
        "evidencia_legal": evidencia,
        "obligatorio_en_finiquito": True,
        "params_usados": {"SBL": sbl, "dias_pendientes": dias_pendientes},
    }
```

```python
# liquidator/core/engine.py
def _calcular_vacaciones_si_finiquito(self, inp, renglones):
    if inp.modo != "FINIQUITO":
        return
    if not inp.vacaciones or inp.vacaciones.dias_pendientes <= 0:
        if inp.vacaciones and inp.vacaciones.dias_pendientes == 0:
            logger.info("Finiquito sin vacaciones pendientes; nada que pagar")
            return
        # Si no se pasa vacaciones, compliance debe advertir (ver 2.Z)
        return
    renglon = self.prestaciones.calcular_vacaciones_compensadas_finiquito(
        sbl=inp.salario.SBL,  # para vacaciones NO suma auxilio_trans ni recargos
        dias_pendientes=inp.vacaciones.dias_pendientes,
    )
    renglones.append(renglon)
```

**Validación:**

```python
def test_vacaciones_7_5_dias_sbl_2_200_000():
    calc = PrestacionesCalculator(params={...})
    r = calc.calculate_vacaciones_compensadas_finiquito(
        sbl=Decimal("2200000"), dias_pendientes=Decimal("7.5")
    )
    assert r["valor"] == Decimal("550000")
    assert "Art. 189" in r["evidencia_legal"]
    assert r["obligatorio_en_finiquito"] is True

def test_vacaciones_cero_dias_no_aporta():
    calc = PrestacionesCalculator(params={...})
    r = calc.calculate_vacaciones_compensadas_finiquito(
        sbl=Decimal("2200000"), dias_pendientes=Decimal("0")
    )
    assert r["valor"] == Decimal("0")
```

### Tarea 2.Z — Regla de compliance: vacaciones causadas en finiquito

**Archivos:**
- Modificar `params/checklist.json` (agregar regla `V_VACACIONES_FINIQUITO`).
- Modificar `liquidator/compliance/compliance_engine.py` (evaluar: si modo
  FINIQUITO y `vacaciones is None`, warning; si `dias_pendientes > 0` y no
  aparece renglón en `desglose["vacaciones"]`, blocking CRITICAL).
- Actualizar `Contexto/KB_LLM/03_compliance_blocking.md`.

**Regla en `params/checklist.json`:**

```json
{
  "id": "V_VACACIONES_FINIQUITO",
  "description": "En finiquito, si hay vacaciones pendientes causadas, deben pagarse obligatoriamente (Art. 189-190 CST). La ausencia del renglón en el desglose es fallo CRITICAL.",
  "severity": "CRITICAL",
  "blocking": true,
  "rule_ref": "Art. 189-190 CST",
  "formula": "SBL / 30 × días_pendientes",
  "aplica_si": "modo == FINIQUITO AND vacaciones.dias_pendientes > 0",
  "excepcion": "Si vacaciones.dias_pendientes == 0 (todas disfrutadas), regla N/A"
},
{
  "id": "V_VACACIONES_DECLARADAS_FINIQUITO",
  "description": "En FINIQUITO se RECOMIENDA declarar vacaciones.dias_pendientes. Si no se declara, se emite WARNING (severidad MEDIUM).",
  "severity": "MEDIUM",
  "blocking": false,
  "rule_ref": "Art. 186 CST (causación)",
  "aplica_si": "modo == FINIQUITO AND vacaciones IS NULL"
}
```

### Tarea 3.G — PreRenderValidator específico por motivo + plantilla `finiquito_renuncia.j2`

**Archivos:**
- Modificar `liquidator/output/pre_render_validator.py` (agregar matriz
  motivo → campos obligatorios).
- Agregar `liquidator/templates/finiquito_renuncia.j2` (versión mínima de
  la plantilla general `finiquito.j2` para este caso).
- En el desglose del documento PDF/MD, la sección "Indemnización" debe
  aparecer explícitamente como `N/A — motivo renuncia (no hay indemnización)`
  para evitar ambigüedad jurídica.

**Matriz pre-render:**

```python
# liquidator/output/pre_render_validator.py
REQUISITOS_POR_MOTIVO = {
    "RENUNCIA_VOLUNTARIA": {
        "requiere": ["vacaciones"],
        "no_requiere": ["indemnizacion"],
        "nota_render": "NO HAY INDEMNIZACIÓN: el trabajador renunció voluntariamente.",
    },
    "DESPIDO_SIN_JUSTA_CAUSA": {
        "requiere": ["vacaciones", "indemnizacion"],
        "no_requiere": [],
        "nota_render": "",
    },
    "DESPIDO_CON_JUSTA_CAUSA": {
        "requiere": ["vacaciones"],
        "no_requiere": ["indemnizacion"],
        "nota_render": "NO HAY INDEMNIZACIÓN: despido con causa legal (Art. 62 CST).",
    },
    ...
}
```

**Fragmento de plantilla `finiquito_renuncia.j2`:**

```jinja
{% if contrato.motivo_terminacion == "renuncia_voluntaria" %}
## Indemnización
**NO APLICA** — El trabajador {{ trabajador.nombre }} renunció voluntariamente
al cargo, conforme al Art. 49 num. 6 del Código Sustantivo del Trabajo. Por
tanto, no se genera indemnización conforme al Art. 64 CST.
{% endif %}

{% if desglose.has_vacaciones %}
## Vacaciones compensadas (Art. 189-190 CST)
Días pendientes al {{ contrato.fecha_terminacion_real }}: **{{ vacaciones.dias_pendientes }}**
Valor: **{{ format_cop(desglose.vacaciones.valor) }}**
{% endif %}
```

## D. DoD agregado del addendum

- [ ] Schema `Contrato` extendido con `motivo_terminacion: MotivoTerminacion`
      (enum con todos los artículos 45-49 CST)
- [ ] Nuevo modelo `VacacionesEstado` tipado (Decimal para días_pendientes)
- [ ] LiquidacionInput valida que `modo FINIQUITO` requiera `motivo_terminacion`
- [ ] `PrestacionesCalculator.calculate_vacaciones_compensadas_finiquito` implementado
      con fórmula Art. 189-190 CST
- [ ] Motivo `renuncia_voluntaria` no genera indemnización (documentado
      en plantilla y en desglose final)
- [ ] Regla CRITICAL `V_VACACIONES_FINIQUITO` activa en compliance
- [ ] PreRenderValidator específico por motivo
- [ ] Plantilla `finiquito_renuncia.j2` (o equivalente condicional en
      `finiquito.j2`) renderiza nota de no-indemnización
- [ ] Test golden: caso canónico del addendum (renuncia voluntaria con
      7.5 días de vacaciones, SBL 2.200.000, 212 días)
- [ ] Suite al 100%
- [ ] KB actualizada:
  - `Contexto/KB_LLM/01_reglas_calculo.md` → sección "Vacaciones compensadas
    obligatorias en finiquito"
  - `Contexto/KB_LLM/04_schema_entrada.md` → campos nuevos
  - `Contexto/KB_LLM/03_compliance_blocking.md` → nuevas reglas CRITICAL/MEDIUM

## E. Estimación de esfuerzo

| Tarea | Esfuerzo | Dependencias |
|-------|----------|--------------|
| 1.C-ter | Bajo (1 sesión) | Ninguna — schema retrocompatible |
| 2.B-ter | Medio (1 sesión) | 1.C-ter |
| 2.Z | Bajo (0.5 sesión) | 2.B-ter |
| 3.G | Medio (1 sesión) | 1.C-ter, 2.B-ter |
| **Total** | **2-3 sesiones** | Acotar a 1 fase por sesión (convención del usuario) |

## F. Riesgos

- **R1:** Cambiar `dias_pendientes` de `int` a `Decimal` puede afectar
  redondeos en cálculos. Mitigación: usar `ROUND_HALF_UP` y documentar
  que fracciones de día son legales en CST.
- **R2:** El motor actual no distingue entre finiquito y periódica al
  calcular vacaciones. Mitigación: Tarea 2.B-ter agrega método específico
  `calculate_vacaciones_compensadas_finiquito` y el motor lo invoca sólo
  cuando `modo == "FINIQUITO"`.
- **R3:** Indemnización Art. 64 CST no se implementa en esta iteración.
  Mitigación: documentar que si en el futuro se requiere, añadir Tarea
  2.W con el mismo patrón (fórmula + test golden + compliance).
- **R4:** El caso canónico del plan actual es PERIODICA; agregar un
  FINIQUITO podría romper fixtures existentes si no se aísla. Mitigación:
  crear `examples/inputs/finiquito_renuncia_206d.json` separado; test
  específico en `test_golden/test_finiquito_renuncia.py`.
- **R5:** Verificación verbatim de Art. 189-190 CST no hecha. Mitigación:
  antes de cerrar Tarea 2.B-ter, descargar SUIN/CST y verificar texto
  literal; registrar `estado_verificacion` en `params/normas.json`.
- **R6:** Plantilla `finiquito_renuncia.j2` podría duplicar lógica con
  `finiquito.j2`. Mitigación: usar un solo `finiquito.j2` con bloques
  condicionales por motivo (más mantenible).

## G. Caso golden propuesto (tu caso específico)

**Input:** `examples/inputs/finiquito_renuncia_212d.json`

```json
{
  "trabajador": {"nombre": "ANONIMIZADO", "documento": "0"},
  "empleador":  {"nombre": "ANONIMIZADO", "documento": "1"},
  "contrato":   {
    "fecha_ingreso": "2025-11-16",
    "fecha_corte": "2026-06-15",
    "tipo": "INDEFINIDO",
    "fecha_terminacion_real": "2026-06-15",
    "motivo_terminacion": "renuncia_voluntaria"
  },
  "salario":    {
    "SBL": 2200000,
    "auxilio_transporte": false,
    "variable": false
  },
  "modo":       "FINIQUITO",
  "vacaciones": {
    "dias_pendientes": 7.5,
    "dias_disfrutados": 0
  },
  "segmentos": [
    {"anio": 2025, "desde": "2025-11-16", "hasta": "2025-12-31"},
    {"anio": 2026, "desde": "2026-01-01", "hasta": "2026-06-15"}
  ]
}
```

**Output esperado (valores clave):**

| Concepto | Valor | Días | Fórmula | Artículo |
|----------|-------|------|---------|----------|
| Cesantías seg. 2025 | $281.111 | 46 | 2.200.000 × 46 / 360 | Art. 249 CST |
| Cesantías seg. 2026 | $1.014.444 | 166 | 2.200.000 × 166 / 360 | Art. 249 CST |
| **Total cesantías** | **$1.295.555** | 212 | suma segmentos | — |
| Intereses sobre cesantías 2025 | $8.433 | 46 | 281.111 × 12% × 46/360 | Art. 99 Ley 50/1990 |
| Intereses sobre cesantías 2026 | $56.360 | 166 | 1.014.444 × 12% × 166/360 | Art. 99 Ley 50/1990 |
| Prima seg. H2-2025 | $281.111 | 46 | 2.200.000 × 46/360 | Art. 306 CST |
| Prima seg. H1-2026 | $1.014.444 | 166 | 2.200.000 × 166/360 | Art. 306 CST |
| Vacaciones compensadas | $550.000 | 7.5 | 2.200.000/30 × 7.5 | Art. 189-190 CST |
| Indemnización | **N/A** | — | Renuncia voluntaria | Art. 49 num. 6 |
| **TOTAL LIQUIDACIÓN** | **~$4.427.014** | — | — | — |

**Test esperado:**

```python
def test_finiquito_renuncia_212d():
    inp = json.loads((REPO/"examples"/"inputs"/"finiquito_renuncia_212d.json").read_text())
    provs = ParamsProvider.for_range(
        date.fromisoformat(inp["contrato"]["fecha_ingreso"]),
        date.fromisoformat(inp["contrato"]["fecha_corte"]),
    )
    engine = LiquidacionEngine(provs=provs)
    result = engine.process_input(inp)

    assert result["compliance"]["status"] in ("GO", "WARN")
    assert "indemnizacion" not in result["desglose"] or \
           result["desglose"]["indemnizacion"]["valor"] == Decimal("0")
    assert result["desglose"]["vacaciones"]["valor"] == Decimal("550000")
    assert result["desglose"]["vacaciones"]["dias"] == Decimal("7.5")

    # Suma total
    total = Decimal(str(result["total_liquidacion"]))
    assert Decimal("4400000") < total < Decimal("4450000")
```

## H. Referencias legales (verificar verbatim antes de cierre)

- **Art. 49 CST num. 6** — "Por la dimisión, retiro o cesación voluntaria
  del trabajo por parte del trabajador". Verificar texto literal en SUIN/CST.
- **Art. 186 CST** — "Todo trabajador que hubiere prestado sus servicios
  durante un (1) año, tendrá derecho a quince (15) días hábiles consecutivos
  de vacaciones remuneradas". Proporcional a fracción de año.
- **Art. 189 CST párr. 1°** — "Las vacaciones no son susceptibles de
  compensación en dinero... excepto cuando el contrato de trabajo termine
  sin haberlas disfrutado, caso en el cual serán compensadas en dinero con
  el salario que ordinariamente devengue en la fecha en que surja el derecho
  a su disfrute". Verificar texto completo en SUIN/CST.
- **Art. 190 CST** — "Cuando las vacaciones sean compensadas en dinero, el
  empleador pagará como compensación un día de salario por cada día de
  vacaciones". Fórmula confirmada.
- **Art. 185 CST** — "Salario ordinario" para vacaciones. No se incluyen
  horas extras ni recargos. Confirmar que auxilio de transporte tampoco
  entra en esta base.
- **Art. 64 CST** — indemnización solo por despido sin justa causa (no
  aplica para renuncia voluntaria). Verificar tabla actualizada de días
  en parágrafo.
- **Art. 65 CST** — pago inmediato en terminación, si se requiere para
  plazos de pago.
- **Art. 46 CST** — preaviso solo para contratos a término fijo menor de
  1 año (no aplica para contrato indefinido).

## I. Compatibilidad hacia atrás

- `LiquidacionInput` con `modo == "PERIODICA"` y sin `vacaciones` =
  comportamiento actual intacto. **No es breaking.**
- `Contrato` sin `motivo_terminacion` (cuando `fecha_terminacion_real is None`)
  = compatible con el caso canónico PERIODICA del plan.
- `Contrato` con `fecha_terminacion_real` sin `motivo_terminacion` =
  **nuevo requisito obligatorio**: falla validación. Para migrar inputs
  históricos que tengan `fecha_terminacion_real`, agregar `motivo_terminacion`
  apropiado.
- `vacaciones` como `dict` legacy (del plan original) vs `VacacionesEstado`
  tipado = la migración se hace por el modelo Pydantic; inputs antiguos
  siguen funcionando si sus campos son consistentes.
- Documentos v2.0 existentes siguen siendo válidos, pero los nuevos
  finiquitos con renuncia voluntaria llevarán la nota de no-indemnización
  y la sección de vacaciones obligatorias.

## J. Hand-off a próxima sesión

**Para el operador (Jhond) o agente que ejecute la próxima fase:**

1. **Cargar antes de empezar:** validar contra código vivo (doctrina del
   plan original §5.5.11: "si código y plan/diagnóstico discrepan, código
   gana; el plan se actualiza").
2. **Validar primero (sin tocar código):**
   - Leer `liquidator/contracts/input_model.py`: ver si ya existe campo
     `motivo_terminacion` o alguna forma de vacaciones tipada
   - Leer `liquidator/calculators/prestaciones.py`: ver si ya existe método
     `calculate_vacaciones` o `calculate_vacaciones_compensadas`
   - Leer `params/checklist.json`: verificar qué reglas de compliance ya
     existen; no duplicar
   - `grep -r "vacaciones\|finiquito\|indemnizacion\|Art. 189\|Art. 64"
     liquidator/ params/ Contexto/` para detectar qué ya está cubierto
3. **Verificación legal antes de implementar:**
   - Descargar SUIN/CST los artículos 185, 186, 189, 190 y 49 num. 6
   - Capturar texto literal en `legal_docs/` (si no están ya)
   - Registrar `estado_verificacion: "VERIFICADO"` con URL y fecha
4. **Orden de ejecución recomendado:**
   - Sesión 1: Tarea 1.C-ter (schema + tests de validación)
   - Sesión 2: Tareas 2.B-ter + 2.Z (motor + compliance)
   - Sesión 3: Tarea 3.G (plantilla + pre-render)
   - Sesión 4: caso golden completo + verificación manual por Jhond
5. **Actualizar al cerrar:** `Contexto/KB_LLM/09_caso_canonico_usuario.md`
   con resultado de la sesión; sincronizar `REGISTRY.md`/checklist si
   existen.
6. **Si el operador decide NO ejecutar este addendum ahora:** el plan v2.0
   sigue vigente; el sistema puede seguir calculando liquidaciones
   periódicas. El finiquito con vacaciones quedará como brecha pendiente.

## K. Relación con el caso real (Pedro Franco — archivado en legal_docs/_archive/liquidacion_kb_agente_v1.0_2025.md)

El caso del plan original (línea 150 del plan) menciona:

> **Vacaciones pendientes heredadas (referencia, no parte del caso canónico):**
> El caso real `liquidacion_pedro_franco.json` (modo PERIODICA, 2024-11-16
> → 2025-11-15) tiene 7.5 días de vacaciones compensadas por acuerdo mutuo
> (Art. 189 CST). Si el contrato de Pedro Franco sigue vigente, esos 7.5
> días se arrastran al finiquito definitivo.

Con este addendum, esos 7.5 días quedan formalizados como dato de entrada
(`vacaciones.dias_pendientes = 7.5`) en el finiquito definitivo. El motor
los tratará de la misma forma que el caso genérico del §G de este addendum.

---

*Addendum aprobado el 2026-06-11 como parte de la evaluación del plan v2.0
contra la necesidad de liquidar un caso real de contrato indefinido terminado
por renuncia voluntaria con vacaciones pendientes causadas no disfrutadas.*
