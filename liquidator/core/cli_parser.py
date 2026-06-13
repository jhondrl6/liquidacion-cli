#!/usr/bin/env python3
"""
Parser ASCII para liquidar - puede ser importado desde bin/liquidar
o desde core/engine si se prefiere.
"""
import argparse


def build_parser():
    """Devuelve parser con TODOS los flags de la SESION 13 - ASCII puro."""
    p = argparse.ArgumentParser(
        prog="liquidar", description="Liquidacion nomina Colombia 2025"
    )
    p.add_argument("--input", "-i")
    p.add_argument("--output", "-o")

    p.add_argument("--modo", choices=["PERIODICA", "FINIQUITO"])
    p.add_argument("--fecha_ingreso")
    p.add_argument("--fecha_corte")
    p.add_argument("--salario_mensual", type=int)
    p.add_argument("--reside_en_lugar_trabajo", type=lambda x: x.lower() == "true")
    p.add_argument("--auxilio_conectividad", type=int, default=0)
    p.add_argument("--tipo_contrato", choices=["indefinido", "fijo"])

    p.add_argument(
        "--enforce-compliance", type=lambda x: x.lower() == "true", default=True
    )
    p.add_argument(
        "--compliance-policy",
        choices=["lenient", "standard", "strict"],
        default="standard",
    )
    p.add_argument("--human-override", action="store_true")
    p.add_argument("--operator-id")
    p.add_argument("--override-reason")

    p.add_argument("--test-run", action="store_true")
    p.add_argument("--generate-pdf")
    p.add_argument("--compliance-check-only")
    return p
