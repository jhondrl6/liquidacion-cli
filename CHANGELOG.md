# Changelog
## Colombia Payroll Settlement System 2025

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added (Fase 0 — Higiene + segundo cerebro mínimo)
- **`Contexto/KB_LLM/`**: 9 notas sustantivas creadas (00-09) — segundo cerebro local versionado en Markdown.
  - `00_fuente_de_verdad.md` — jerarquía de verdad (código > params > tests > legal > docs).
  - `01_reglas_calculo.md` — fórmulas de cesantías, intereses (12%), prima, vacaciones; indemnización Art. 64 referenciada pero NO implementada.
  - `02_parametros_vigentes.md` — SMMLV/aux_trans/tasas por año (2025 y 2026) con cita a decreto y regla de selección por `fecha_corte`.
  - `03_compliance_blocking.md` — estados GO/WARN/NO_GO/OVERRIDE_APPROVED, mecánica de V001-V010 y de override.
  - `04_schema_entrada.md` — Forma 1 (input informal) y Forma 2 (input segmentado por año).
  - `05_schema_salida.md` — shape del `liquidacion_result.json` con `meta.parametros_por_segmento` por año.
  - `06_riesgos_modelo.md` — 12 riesgos tipificados (R-LEG-01 a R-SEC-01).
  - `07_checklist_generacion_liquidacion.md` — 17 pasos operativos pre/durante/post corrida.
  - `08_arquitectura_segundo_cerebro.md` — 6 capas, decisión explícita de NO fine-tuning.
  - `09_caso_canonico_usuario.md` — caso ancla (SBL 2.200.000, 206 días, 2 segmentos) pendiente de ejecución end-to-end en Fase 1.
- Decisión documentada: prescripción usa **Art. 488 CST** (no Art. 155). Repar bloqueante de addendum SL2630-2024.
- **`AGENTS.md`** (183 líneas): reglas inamovibles para agentes (jerarquía de verdad de 6 niveles, 12 reglas operativas, 14 trampas conocidas, tabla de referencias rápidas). Creado en S7 (Tarea 0.G).\n- **`Contexto/prompts/`**: 3 prompts operativos para sesiones LLM (581 líneas totales).
  - `prompt_generacion_liquidacion.md` (171 líneas) — workflow A/B/C (pre-cálculo, cálculo, post-cálculo) + jerarquía de verdad + 10 reglas inamovibles + formato de respuesta obligatorio.
  - `prompt_auditoria_antes_de_responder.md` (176 líneas) — 5 pasos de auditoría, formato con evidencia verbatim (archivo:línea), lista de "lo que NUNCA debés hacer" (no inventar URLs SUIN, no aceptar doc como verdad, etc.).
  - `prompt_plan_modernizacion.md` (234 líneas) — verificación contra disco, decisión "1 fase por sesión" como máximo, decisiones vigentes de los 2 addendas + 11 trampas conocidas.
- **`scripts/check_kb_freshness.py`** + **`liquidator/tests/test_kb_freshness.py`** (S8 — Tarea 0.H): script year-aware (157 líneas) + suite de 6 tests (189 líneas) que verifican que `params/<año>.json` y KB_LLM/02_parametros_vigentes.md estén sincronizados para cualquier año.
- **`AGENTS.md`** ya en raíz (S7 — Tarea 0.G).
- **`git init`** + commit inicial `f04d639` con 200 archivos / 43.477 insertions (S9 — Tarea 0.I). Working tree clean except 3 untracked intencionales (logs pre-2026 + `.env.backup_pre_rotation_2026-06-12`).
- **Suite `pytest` inventariada (S10 — Tarea 0.J)**: comando del plan §5.2 T0.J corrido en WSL con `uv run --with pytest ...`. Resultado: 257 collected, 182 passed (70.8%), 52 failed, 23 errors (8 collection + 15 runtime), 1 warning. **75 issues preexistentes** documentados en `Contexto/KB_LLM/06_riesgos_modelo.md` §R-OP-02 agrupados en 13 causas raíz. Asignación 100% a Fase 1 (17 a 1.A-1.B, 27 a 1.C-1.D, 31 a 1.F-1.H). Suites de 0.A-0.I re-validadas: 62/63 verde.

### Pending (próximas sesiones de Fase 0)
- 0.K: `KB_LLM/02_parametros_vigentes.md` con tabla comparativa 2025 vs 2026 (deja KB y `params/` listos; cambio REAL del motor a `ParamsProvider` year-aware es Tarea 1.E de Fase 1).

---

## [1.0.0] - 2025-11-04

### Added
- **Complete Settlement System**: Full implementation for Colombian payroll social benefits calculations
- **Dual Calculation Modes**: 
  - PERIODICA mode for ongoing social benefits
  - FINIQUITO mode for contract termination calculations
- **Comprehensive Calculators**:
  - Salario Base de Liquidación (SBL) calculator with multiple variants
  - Cesantías and Intereses calculator
  - Prima de Servicios calculator  
  - Vacaciones calculator with compensation features
  - Indemnización calculator with legal limit enforcement
- **Legal Compliance Engine**:
  - 10-point compliance checklist (V001-V010) based on Colombian labor law
  - Automated compliance validation against legal requirements
  - Override system with justification tracking
  - Comprehensive compliance reporting
- **Security Framework**:
  - Input validation with injection attack prevention
  - Data sanitization and sensitive data masking
  - Security monitoring with threat detection
  - Rate limiting and failed attempt tracking
- **Production Monitoring**:
  - Structured logging with JSON format
  - Health check system with component validation
  - Performance metrics collection
  - Memory, CPU, and disk usage monitoring
- **Output Generation**:
  - JSON structured outputs with full audit trail
  - Markdown document generation
  - PDF generation with professional formatting
  - Template system for customizable outputs
- **Audit System**:
  - Hash-based input/output verification
  - Complete audit trail generation
  - Version tracking for reproducibility
  - Compliance audit logging
- **CLI Interface**:
  - Complete command-line argument handling
  - File-based and parameter-based input support
  - Special modes (test, PDF generation, compliance-only)
- **Configuration Management**:
  - Environment-specific configurations (development/production)
  - YAML-based configuration files
  - Runtime parameter override capability
- **Production Readiness**:
  - Production-optimized configuration
  - Security hardening recommendations
  - Backup and recovery procedures
  - Monitoring and alerting setup

### Legal Coverage (2025)
- **Código Sustantivo del Trabajo** implementation:
  - Articles 64-65 (Indemnizaciones y plazos de pago)
  - Articles 186-192 (Vacaciones)
  - Articles 249-250 (Cesantías y regímenes)
  - Articles 306-308 (Prima de servicios)
- **Ley 50 de 1990** (Tasa de intereses de cesantías: 12%)
- **Decreto 1572 de 2024** (SMMLV 2025: $1,423,500)
- **Decreto 1573 de 2024** (Auxilio de transporte 2025: $200,000)
- **Decreto 2466 de 2025** (Nuevos recargos dominicales 80% desde 2025-07-01)

### Special Cases Handled
- **Trabajadores de finca rural**: Proper handling of transportation allowance exclusion
- **Salario variable**: 12-month averaging calculation implemented
- **Auxilio de conectividad**: Validation rules and documentation requirements
- **Cálculo proporcional**: Semi-proportional calculations for partial periods
- **Topes legales**: 20 SMMLV indemnization limit enforcement

### Technical Architecture
- **Modular Design**: Separate modules for calculators, compliance, validation, and output
- **Testing Suite**: 85%+ code coverage with comprehensive test cases
- **Documentation**: Complete API reference, user guide, and developer documentation
- **Type Safety**: Full type hints for maintainability and reliability

### Security Features
- **Input Validation**: Protection against SQL injection, XSS, and command injection
- **Data Protection**: Sensitive data masking in logs and outputs
- **Access Control**: Rate limiting and automated blocking for suspicious activity
- **Audit Security**: Immutable audit trails with hash verification

### Production Features
- **Monitoring**: Real-time health checks and performance metrics
- **Logging**: Structured JSON logging with log rotation
- **Backups**: Automated backup system with recovery procedures
- **Deployment**: Complete deployment guide with production configuration
- **Dependencies**: PyPI package distribution with dependency management

### Documentation
- **API Reference**: Complete documentation of all modules and functions
- **User Guide**: Step-by-step usage instructions with examples
- **Developer Guide**: Architecture overview and contribution guidelines
- **Deployment Guide**: Production deployment procedures and best practices
- **Legal Documentation**: Mapping of calculations to legal references

### Legal Disclaimer
- Comprehensive legal disclaimer
- Use limitation notifications
- Professional supervision recommendations
- No warranty clarifications

---

## Version Policy
This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes or major new features
- **MINOR**: New features in a backwards compatible manner
- **PATCH**: Backwards compatible bug fixes

### Release Schedule
- **Major releases**: Annually with parameter updates
- **Minor releases**: Quarterly with feature improvements
- **Patch releases**: As needed for bug fixes and security updates

### Maintenance Windows
- **Parameter updates**: January 1st each year (aligned with SMMLV updates)
- **Compliance updates**: As required by legal changes
- **Security patches**: Within 30 days of vulnerability discovery

---

## Support
For support, bug reports, or feature requests, please refer to the project documentation and support channels.

---

*This changelog covers changes from the initial development to production release. For future changes, please refer to subsequent entries.*
