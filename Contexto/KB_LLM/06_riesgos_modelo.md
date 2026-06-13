# 06 — Riesgos del modelo (saber dónde NO confiar)

> Lista viva de riesgos conocidos. Cada riesgo tiene severidad, fase
> en la que se aborda, y referencia al lugar donde se documenta o se
> decide. Esta nota NO es un changelog de bugs: es un mapa de qué
> partes del modelo se sabe que son frágiles o están incompletas.

## R-LEG-01 — Indemnización Art. 64 CST no implementada en v2.0

- **Severidad:** ALTA (legal).
- **Estado v2.0:** NO IMPLEMENTADO. Reparo (c) del addendum finiquito.
  El motor no emite valores de indemnización; queda referenciada en
  `01_reglas_calculo.md` y `params/normas.json` (entrada `CST_64`)
  para casos futuros (Fase 4+).
- **Implicación:** si un usuario pide una liquidación por despido sin
  justa causa, el output dará `indemnizacion: null` y el SBL
  correspondiente a esa prestación NO estará en `total_liquidacion`.
  El compliance debería levantar `WARN` o `NO_GO` (decisión de
  producto pendiente en Fase 1).
- **Mitigación temporal:** documentar prominentemente en el MD/PDF
  generado que la indemnización no está incluida y debe calcularse
  por separado. En CLI: emitir exit code 2 + mensaje claro si
  `motivo_terminacion == DESPIDO_SIN_JUSTA_CAUSA` (flag pendiente en
  Tarea 1.C-ter).

## R-LEG-02 — Prescripción: usar Art. 488 CST, NO Art. 155 CST

- **Severidad:** CRÍTICA (error conceptual pre-existente).
- **Origen:** el addendum SL2630-2024 (reparo a) detectó que el
  plan inicial usaba Art. 155 CST para prescripción de prestaciones,
  lo cual es incorrecto. **Art. 155 CST** se refiere a la
  prescripción de acciones derivadas del contrato de trabajo en
  general (3 años); **Art. 488 CST** es el término especial de
  prescripción para prestaciones sociales (3 años contados desde
  cuando la prestación se hizo exigible).
- **Estado v2.0:** TODO el código y la KB deben citar Art. 488 CST
  para prescripción de prestaciones. Cero referencias a Art. 155 CST
  en este contexto.
- **Acción:** grep en `liquidator/`, `params/`, `Contexto/`,
  `Planificación/` por `Art. 155` y `Art\\.\\s*155`; cada match debe
  ser revisado y reemplazado o justificado. Verificar antes de
  cerrar Fase 2-bis (addendum SL2630-2024) DoD.

## R-LEG-03 — SL2630-2024 citada como PENDIENTE en el diagnóstico

- **Severidad:** ALTA (legal).
- **Origen:** la Sentencia Laboral SL2630-2024 (Sala Laboral, sobre
  indexación de prestaciones prescritas) se referencia en el plan y
  en el diagnóstico pero su texto literal, sala y URL oficial
  pendientes de verificación. Reparo (b) del addendum SL2630-2024.
- **Estado v2.0:** la regla `V_INDEXACION_IPC` aún no existe en
  `params/checklist.json`. La entrada de `params/normas.json` con
  `id: SL2630_2024` aún no se ha creado con `estado_verificacion:
  "VERIFICADO"`. Está planificado para Fase 2-bis.
- **Mitigación:** NO usar la SL2630-2024 como soporte de cálculo
  alguno en v2.0. Si surge duda legal sobre indexación, dejar el
  output con `indemnizacion_indexada: null` y `warnings: [...]`.

## R-LEG-04 — Art. 189 CST párr. 1° no verificado en SUIN

- **Severidad:** ALTA (legal, bloqueante para 2.B-ter).
- **Origen:** addendum finiquito, reparo (a). El addendum distingue
  dos figuras:
  - **Compensación por acuerdo mutuo** (Art. 189 general): requiere
    solicitud del trabajador + acuerdo escrito.
  - **Compensación obligatoria en finiquito** (Art. 189 párr. 1° +
    Art. 190): el empleador debe pagar en dinero las vacaciones
    causadas y no disfrutadas al terminar el contrato.
- **Estado v2.0:** la entrada `CST_189_VACACIONES` en
  `params/normas.json` **no existe aún**. Se debe crear con
  `estado_verificacion: "VERIFICADO"`, URL SUIN oficial
  (`https://www.suin-juriscol.gov.co/`) y fecha de verificación.
- **Bloqueante:** Tarea 2.B-ter (modo FINIQUITO, vacaciones
  compensadas) no se puede cerrar sin esta verificación.

## R-LEG-05 — URLs de Decretos 1469/2025 y 1470/2025 con placeholder

- **Severidad:** MEDIA (auditoría).
- **Origen:** `params/normas.json` entradas `DECRETO_1469_2025` y
  `DECRETO_1470_2025` tienen `url = "?i=XXXXXX"` (placeholder del
  autor del JSON, no URL real).
- **Acción:** antes de v2.0 release, verificar las URLs reales en
  SUIN y reemplazar. Hasta entonces, el JSON es funcional pero
  rompe cualquier link de auditoría automática.

## R-OP-01 — Clave de cifrado rotada el 2026-06-12

- **Severidad:** MEDIA (seguridad operativa, ya mitigada).
- **Origen:** Tarea 0.A (sesión S1). Clave anterior con SHA256
  `de1b22...8868` invalidada; backup en `.env.backup_pre_rotation_2026-06-12`.
  Asumimos compromiso de la clave anterior.
- **Mitigación:** clave nueva en `.env`, `.env.example` con
  placeholders, `grep` de clave vieja retorna 0.
- **Acción residual:** cualquier dato cifrado con la clave anterior
  (si existe en `data/` o en backups) debe re-cifrarse. Revisar
  `data/` y `audit/` en Fase 0. Si no hay datos cifrados, basta
  documentar que el compromiso se asumió sin datos a re-cifrar.

## R-OP-02 — 13 errores de colección de tests baseline (pendiente Tarea 0.J)

- **Severidad:** MEDIA (cobertura).
- **Origen:** diagnóstico §2.4 documenta 13 errores preexistentes de
  colección de tests al inicio de Fase 0. Tras Tarea 0.D (corregir 5
  SyntaxError) se redujo el número; no se re-cuenta en esta sesión.
- **Acción:** Tarea 0.J — correr suite completa, reducir a 0 o
  documentar cada fallo preexistente con issue → Fase 1.

## R-OP-03 — Inconsistencias de esquema en `auxilio_conectividad`

- **Severidad:** BAJA (input).
- **Origen:** `examples/inputs/finca_rural.json` incluye el campo
  `auxilio_conectividad: 150000` sin que esté claro si entra al SBL
  (es aux_trans legal? es concepto salarial?). El campo no existe
  en la Forma 2 del schema (ver `04_schema_entrada.md`).
- **Acción:** schema Pydantic de Fase 1 (Tarea 1.D) debe decidir:
  (a) descartar el campo con WARN, (b) incluirlo en SBL con flag
  `auxilio_conectivar_legal: bool`, (c) tratarlo como variable. Por
  ahora, el motor real no debe tocarlo.

## R-MOD-01 — Documentación desactualizada (docs/, README, QWEN)

- **Severidad:** MEDIA (consumo humano).
- **Origen:** el repo tiene `docs/`, `README.md` (6239 bytes, dic-2025),
  `QWEN.md` (4615 bytes, nov-2025) y un `Plan de ejecución.md`
  histórico. Reflejan un estado pre-Fase 0.
- **Decisión v2.0:** NO reescritura inmediata. Plan §4 Fase 4
  (release) es cuando se actualizan. Hasta entonces, la KB y
  `REGISTRY.md` son las fuentes vivas.

## R-MOD-02 — Dependencia de LLM externo para algunas funciones

- **Severidad:** MEDIA (operativa).
- **Origen:** el proyecto ha usado LLMs para redactar plantillas,
  sugerir cálculos y revisar compliance. Esto crea dependencia de
  disponibilidad y de calidad.
- **Decisión (diagnóstico §5.10):** NO delegar cálculo numérico al
  LLM. El cálculo es determinístico y debe estar 100% en Python puro.
  El LLM solo assiste en: redacción de plantillas, revisión de
  compliance legible, explicación deWarnings al usuario.

## R-MOD-03 — Fine-tuning NO se usa (decisión explícita)

- **Severidad:** BAJA (estratégica, ya decidida).
- **Origen:** diagnóstico §5.4 evalúa y descarta fine-tuning por:
  coste, volumen de datos insuficiente, riesgo de alucinaciones
  legales, dificultad de auditar.
- **Decisión v2.0:** NO hacer fine-tuning. Toda inteligencia
  operativa viene de la KB (esta carpeta) + retrieval sobre
  `params/` + `legal_docs/`.

## R-SEC-01 — Datos sensibles en KB o logs

- **Severidad:** ALTA (privacidad).
- **Origen:** cualquier ejemplo o caso en esta KB podría, por error,
  incluir nombres, documentos o salarios reales.
- **Mitigación:** regla AGENTS.md #6: "No incluir nombres, documentos
  de identidad, salarios reales o datos sensibles en la KB, logs o
  repo." El caso canónico usa `[ANONIMIZADO]` en trabajador y empleador.
- **Acción:** grep periódico por patrones `\\d{6,12}` (documentos)
  y por nombres propios. Cualquier match se sanitiza o se borra.

## Última validación contra código

- **Fecha:** 2026-06-13 (sesión S5, Tarea 0.E).
- **Verificado:** riesgos R-LEG-01/02/03/04 tienen base documental
  en addendas. R-OP-01 verificado en REGISTRY log S1. Resto inferido
  de la lectura de `params/`, `liquidator/`, plan y diagnóstico.
- **NO verificado:** que el código no tenga referencias a Art. 155
  CST en contexto de prescripción (grep no ejecutado en esta sesión;
  programado para Fase 2-bis).
