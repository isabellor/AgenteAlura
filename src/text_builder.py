import json
from pathlib import Path
import pandas as pd


def safe_value(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def movement_row_to_text(row: pd.Series) -> str:
    """Convierte una fila enriquecida en texto legible para embeddings o búsqueda."""
    return (
        f"Movimiento {safe_value(row.get('ID_MOVIMIENTO'))}. "
        f"Internación {safe_value(row.get('ID_INTERNACION'))}. "
        f"Paciente demo CHIST {safe_value(row.get('CHIST'))}. "
        f"Nombre demo: {safe_value(row.get('NOMBRE'))} {safe_value(row.get('APELLIDO'))}. "
        f"Fecha de movimiento: {safe_value(row.get('FECHA_MOVIMIENTO'))}. "
        f"Tipo de movimiento: {safe_value(row.get('TIPO_MOVIMIENTO'))}. "
        f"Pabellón: {safe_value(row.get('PABELLON'))}. "
        f"Observaciones: {safe_value(row.get('OBSERVACIONES'))}. "
        f"Diagnóstico: {safe_value(row.get('DIAGNOSTICO'))}. "
        f"Estado de internación: {safe_value(row.get('ESTADO'))}. "
        f"Fecha de ingreso: {safe_value(row.get('FECHA_INGRESO'))}. "
        f"Fecha de egreso: {safe_value(row.get('FECHA_EGRESO'))}."
    )


def build_movement_documents(movimientos_enriquecidos: pd.DataFrame) -> list[dict]:
    """Crea documentos con texto y metadatos."""
    documents = []

    for index, row in movimientos_enriquecidos.iterrows():
        doc = {
            "page_content": movement_row_to_text(row),
            "metadata": {
                "source": "movimientos_enriquecidos.csv",
                "row": int(index) + 2,
                "id_movimiento": safe_value(row.get("ID_MOVIMIENTO")),
                "id_internacion": safe_value(row.get("ID_INTERNACION")),
                "chist": safe_value(row.get("CHIST")),
                "tipo_movimiento": safe_value(row.get("TIPO_MOVIMIENTO")),
                "pabellon": safe_value(row.get("PABELLON")),
            },
        }
        documents.append(doc)

    return documents


def save_documents_jsonl(documents: list[dict], output_path: Path = Path("data/processed/documentos_movimientos.jsonl")) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
