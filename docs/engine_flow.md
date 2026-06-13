# Motor Principal de Orquestación

```text
function process_liquidacion(payload):
    params <- load_params(year=2025)
    parsed <- input_parser.parse_payload(payload, params)

    session_id <- uuid4()
    audit_logger.log_start(session_id, parsed.data, params.version)

    workflow <- WorkflowOrchestrator(params)
    workflow_result <- workflow.execute(parsed.data)

    input_hash <- sha256(parsed.data)
    compliance <- compliance_engine.run(
        input_data=parsed.data,
        params=params,
        calculation_result=workflow_result.compliance_payload,
        input_hash=input_hash
    )

    if parsed.data.enforce_compliance AND compliance.status == NO_GO:
        audit_logger.log_complete(session_id, compliance, blocked=True)
        return build_blocked_response(compliance, input_hash, params.version)

    alerts <- merge(workflow_result.alerts, parsed.warnings, parsed.notes)
    calc_results <- workflow_result.calculation_results
    calc_results.validaciones_y_alertas <- alerts

    output <- json_generator.generate_json(parsed.data, calc_results, compliance, params)
    output.validaciones_y_alertas <- alerts
    output.normas_aplicadas <- workflow_result.normas_aplicadas

    compliance.input_hash <- output.meta.input_hash
    compliance.output_hash <- output.meta.output_hash
    compliance.params_version <- params.version

    audit_logger.log_complete(session_id, compliance, blocked=False)
    trail_generator.persist(session_id, parsed.data, output, compliance)

    return output
```
