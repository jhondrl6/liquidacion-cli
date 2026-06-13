# 08 — Arquitectura del segundo cerebro (capas y decisiones)

> Esta nota documenta las **6 capas** del sistema cognitivo que
> soporta `liquidacion_cli` y por qué se decidió NO hacer
> fine-tuning. Fuente: diagnóstico §5.4 y §5.11.

## Capas (de abajo hacia arriba, en orden de autoridad)

1. **Capa 1 — Código vivo (`liquidator/`, `params/`, `tests/`).**
   - Calculadores, normalizadores, compliance, legal repositories.
   - **Determinístico. Sin LLM.** Si un cálculo depende de un LLM, es
     bug.
   - Tests son la red de seguridad de esta capa.
2. **Capa 2 — Segundo cerebro local (`Contexto/KB_LLM/`, esta carpeta).**
   - 9-10 notas en Markdown, versionadas en el repo.
   - Sirven de mapa para que un LLM o un humano nuevo entienda el
     proyecto en 30 minutos sin leer el plan de 3.353 líneas.
   - Reglas duras: cada nota ≤ 200 líneas, lenguaje concreto (cero
     "principios generales"), referencia siempre al archivo y línea
     del código que sostiene la afirmación.
3. **Capa 3 — Memoria del agente (sesión + cross-sesión).**
   - Memoria de sesión: contexto vivo del agente, no persistido por
     defecto.
   - Memoria cross-sesión: solo hechos duraderos (preferencias del
     usuario, hechos del entorno). NO guardar progreso de tareas,
     outcomes de sesión, números de PR, SHAs, "fase N cerrada".
   - Implementado vía tool `memory` de Hermes.
4. **Capa 4 — Skills (procedimientos reutilizables).**
   - `~/.hermes/skills/` con SKILL.md + opcional `scripts/`,
     `references/`, `templates/`.
   - Codifican procedimientos probados (ej: "cómo correr
     `check_kb_freshness.py`", "cómo redactar una nota KB").
   - Una skill por flujo recurrente, no por tarea única.
5. **Capa 5 — Retrieval sobre código y params.**
   - Búsqueda semántica + literal sobre `liquidator/`, `params/`,
     `legal_docs/`, `Contexto/`.
   - El LLM NO "recuerda" los datos; los busca cuando los necesita.
   - Implementable con `search_files` (regex/ripgrep) o un índice
     vectorial externo (no usado en v2.0; ver R-MOD-03).
6. **Capa 6 — Validación automatizada.**
   - Tests unitarios (`tests/`).
   - Golden tests del caso canónico (`examples/expected/`).
   - `scripts/check_kb_freshness.py` (Tarea 0.H).
   - Compliance checks del motor (`liquidator/compliance/`).

## Por qué NO fine-tuning (decisión explícita)

El diagnóstico §5.4 evalúa 5 opciones de "memoria" del agente y
rechaza fine-tuning por las siguientes razones (resumidas):

| Razón                          | Implicación práctica                                     |
|--------------------------------|----------------------------------------------------------|
| Coste de entrenamiento         | No hay GPU dedicada; el costo-beneficio no cierra.       |
| Volumen de datos insuficiente  | Pocos casos reales firmados por el usuario.              |
| Riesgo de alucinaciones legales| Un modelo que invente un artículo CST es un peligro.     |
| Dificultad de auditar          | Cada predicción debe poder trazarse a una fuente.        |
| Reentrenamiento por cambio legal| Cada decreto nuevo obligaría reentrenar. Inaceptable.    |

**Lo que se hace en su lugar:** retrieval + KB + reglas determinísticas
en código. La inteligencia del agente se invierte en redactar bien
las notas (Capa 2) y los prompts de `Contexto/prompts/`
(Tarea 0.F), no en entrenar pesos.

## Criterios de aceptación del segundo cerebro

Para considerar que la KB cumple su rol, debe:

- [x] Tener 9-10 notas sustantivas (esta carpeta, 00-09, creadas en
      sesión S5 Tarea 0.E).
- [ ] Tener fecha de "última validación" en cada nota, <30 días.
- [ ] Ser referenciada en el primer párrafo de `AGENTS.md` (Tarea 0.G).
- [ ] Ser auto-validable: `scripts/check_kb_freshness.py` puede
      detectar si una nota está desactualizada vs params (Tarea 0.H).
- [ ] NO contener datos sensibles (verificado por grep, regla
      AGENTS.md #6).
- [ ] NO contradecir el código (verificado por re-lectura periódica;
      ver `00_fuente_de_verdad.md`).

## Flujo de uso esperado

```
┌──────────────┐
│  Usuario /   │
│  Operador    │
└──────┬───────┘
       │ sesión nueva
       ▼
┌──────────────────┐    lee jerarquía
│ Lee REGISTRY.md  │ ──────────────┐
│ (estado actual)  │               │
└──────┬───────────┘               │
       │                           ▼
       │                  ┌─────────────────┐
       │                  │ AGENTS.md       │
       │                  │ (12 reglas)     │
       │                  └────────┬────────┘
       │                           │
       │ lee KB (esta carpeta)     │
       │ ◄─────────────────────────┘
       │
       ▼
┌──────────────────┐
│ Corre motor      │ → params/<año>.json
│ con input        │ → legal_docs/
│                  │ → tests/
└──────┬───────────┘
       │ output
       ▼
┌──────────────────┐
│ Compliance check │ → params/checklist.json
│ (V001-V010)      │ → si NO_GO + override: OverrideRecord
└──────┬───────────┘
       │ GO/WARN/NO_GO/OVERRIDE
       ▼
┌──────────────────┐
│ Genera           │ → output/<caso>.json (+.md, +.pdf en Fase 3+)
│ artefactos       │ → artifacts/audit/<ts>.json (Fase 3+)
└──────────────────┘
```

## Última validación contra código

- **Fecha:** 2026-06-13 (sesión S5, Tarea 0.E).
- **Verificado:** las 6 capas existen físicamente en el repo
  (código, KB, memoria cross-sesión activa, skills_list, search_files,
  tests + scripts de validación). Decisión de no-fine-tuning
  reflejada en diagnóstico §5.4.
- **NO verificado:** el test de 30 días de la KB (no ha pasado
  suficiente tiempo desde creación de las notas para que esté
  vencido). El primer chequeo será en sesión ~mediados de julio
  2026.
