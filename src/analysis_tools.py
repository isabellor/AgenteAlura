import re
import pandas as pd


def top_counts(series: pd.Series, n: int = 5) -> str:
    counts = series.dropna().value_counts().head(n)
    if counts.empty:
        return "No hay datos disponibles para calcular este ranking."
    lines = [f"- {idx}: {val}" for idx, val in counts.items()]
    return "\n".join(lines)


def answer_with_pandas(question: str, data: dict[str, pd.DataFrame]) -> str:
    """Responde preguntas frecuentes usando Pandas.

    Esta función es un MVP: usa reglas simples por palabras clave.
    Más adelante puede convertirse en herramientas LangChain.
    """
    q = question.lower()
    pacientes = data["pacientes"]
    internaciones = data["internaciones"]
    movimientos = data["movimientos"]

    if "resumen" in q or "ejecutivo" in q:
        activas = int(internaciones["FECHA_EGRESO"].isna().sum()) if "FECHA_EGRESO" in internaciones.columns else 0
        return (
            f"Resumen del dataset sintético:\n"
            f"- Pacientes demo: {len(pacientes)}\n"
            f"- Internaciones: {len(internaciones)}\n"
            f"- Movimientos: {len(movimientos)}\n"
            f"- Internaciones activas: {activas}\n\n"
            f"Tipos de movimiento más frecuentes:\n{top_counts(movimientos['TIPO_MOVIMIENTO'])}\n\n"
            f"Diagnósticos más frecuentes:\n{top_counts(internaciones['DIAGNOSTICO'])}"
        )

    if "diagn" in q:
        return "Diagnósticos más frecuentes:\n" + top_counts(internaciones["DIAGNOSTICO"], n=10)

    if "pabell" in q:
        return "Pabellones con más movimientos:\n" + top_counts(movimientos["PABELLON"], n=10)

    if "paciente" in q or "pacientes" in q:
        return f"El dataset contiene {len(pacientes)} pacientes demo."

    if "internacion" in q or "internación" in q or "internaciones" in q:
        if "activa" in q or "activas" in q:
            activas = int(internaciones["FECHA_EGRESO"].isna().sum())
            return f"Hay {activas} internaciones activas en el dataset sintético."
        return f"Hay {len(internaciones)} internaciones registradas."

    if "movimiento" in q or "movimientos" in q:
        return f"Hay {len(movimientos)} movimientos registrados.\n\nDetalle por tipo:\n{top_counts(movimientos['TIPO_MOVIMIENTO'], n=10)}"

    if "traslado" in q:
        cantidad = int((movimientos["TIPO_MOVIMIENTO"].astype(str).str.lower() == "traslado").sum())
        return f"Hay {cantidad} movimientos de tipo Traslado."

    if "alta" in q:
        cantidad = int((movimientos["TIPO_MOVIMIENTO"].astype(str).str.lower() == "alta").sum())
        return f"Hay {cantidad} movimientos de tipo Alta."

    if "deriv" in q:
        cantidad = int(movimientos["TIPO_MOVIMIENTO"].astype(str).str.lower().str.contains("deriv").sum())
        return f"Hay {cantidad} movimientos de derivación."

    match = re.search(r"chist\s*(\d+)", q)
    if match:
        chist = int(match.group(1))
        ints = internaciones[internaciones["CHIST"] == chist]
        if ints.empty:
            return f"No encontré registros para el CHIST {chist}."
        ids = ints["ID_INTERNACION"].tolist()
        movs = movimientos[movimientos["ID_INTERNACION"].isin(ids)].copy()
        lines = [f"Historial del CHIST {chist}:"]
        lines.append(f"- Internaciones encontradas: {len(ints)}")
        lines.append(f"- Movimientos encontrados: {len(movs)}")
        for _, row in movs.sort_values("FECHA_MOVIMIENTO").iterrows():
            lines.append(
                f"  - {row['FECHA_MOVIMIENTO']}: {row['TIPO_MOVIMIENTO']} en {row['PABELLON']}"
            )
        return "\n".join(lines)

    return (
        "Puedo responder consultas sobre cantidad de pacientes, internaciones, "
        "internaciones activas, movimientos, diagnósticos, pabellones, traslados, altas, derivaciones "
        "o historiales por CHIST."
    )
