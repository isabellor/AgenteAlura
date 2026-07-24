from pathlib import Path
import pandas as pd


def validate_relationships(data: dict[str, pd.DataFrame]) -> dict[str, int]:
    """Valida duplicados y relaciones entre tablas."""
    pacientes = data["pacientes"]
    internaciones = data["internaciones"]
    movimientos = data["movimientos"]

    results = {
        "pacientes": len(pacientes),
        "internaciones": len(internaciones),
        "movimientos": len(movimientos),
        "chist_duplicados_pacientes": int(pacientes["CHIST"].duplicated().sum()),
        "id_internacion_duplicados": int(internaciones["ID_INTERNACION"].duplicated().sum()),
        "id_movimiento_duplicados": int(movimientos["ID_MOVIMIENTO"].duplicated().sum()),
        "internaciones_sin_paciente": int((~internaciones["CHIST"].isin(pacientes["CHIST"])).sum()),
        "movimientos_sin_internacion": int((~movimientos["ID_INTERNACION"].isin(internaciones["ID_INTERNACION"])).sum()),
    }
    return results


def enrich_data(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Crea tablas enriquecidas para consulta."""
    pacientes = data["pacientes"].copy()
    internaciones = data["internaciones"].copy()
    movimientos = data["movimientos"].copy()

    if "FECHA_INGRESO" in internaciones.columns and "FECHA_EGRESO" in internaciones.columns:
        internaciones["DIAS_INTERNACION"] = (
            internaciones["FECHA_EGRESO"] - internaciones["FECHA_INGRESO"]
        ).dt.days
        internaciones["ANIO_INGRESO"] = internaciones["FECHA_INGRESO"].dt.year
        internaciones["MES_INGRESO"] = internaciones["FECHA_INGRESO"].dt.month

    if "FECHA_MOVIMIENTO" in movimientos.columns:
        movimientos["ANIO_MOVIMIENTO"] = movimientos["FECHA_MOVIMIENTO"].dt.year
        movimientos["MES_MOVIMIENTO"] = movimientos["FECHA_MOVIMIENTO"].dt.month

    internaciones_completas = internaciones.merge(
        pacientes,
        on="CHIST",
        how="left",
        suffixes=("_INTERNACION", "_PACIENTE"),
    )

    movimientos_enriquecidos = movimientos.merge(
        internaciones_completas,
        on="ID_INTERNACION",
        how="left",
        suffixes=("_MOVIMIENTO", "_INTERNACION"),
    )

    return {
        "pacientes": pacientes,
        "internaciones": internaciones,
        "movimientos": movimientos,
        "internaciones_completas": internaciones_completas,
        "movimientos_enriquecidos": movimientos_enriquecidos,
    }


def save_processed_data(enriched: dict[str, pd.DataFrame], output_dir: Path = Path("data/processed")) -> None:
    """Guarda los CSV procesados."""
    output_dir.mkdir(parents=True, exist_ok=True)
    enriched["pacientes"].to_csv(output_dir / "pacientes_procesados.csv", index=False)
    enriched["internaciones"].to_csv(output_dir / "internaciones_procesadas.csv", index=False)
    enriched["movimientos"].to_csv(output_dir / "movimientos_procesados.csv", index=False)
    enriched["movimientos_enriquecidos"].to_csv(output_dir / "movimientos_enriquecidos.csv", index=False)
