from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza encabezados para evitar errores por espacios o minúsculas."""
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(" ", "_", regex=False)
    )
    return df


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia espacios en columnas de texto."""
    df = df.copy()
    text_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in text_cols:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )
    return df


def parse_dates(df: pd.DataFrame, date_columns: list[str]) -> pd.DataFrame:
    """Convierte columnas de fecha si existen."""
    df = df.copy()
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def load_raw_data(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """Carga los tres CSV principales del proyecto."""
    pacientes = pd.read_csv(raw_dir / "pacientes.csv")
    internaciones = pd.read_csv(raw_dir / "internaciones.csv")
    movimientos = pd.read_csv(raw_dir / "movimientos.csv")

    pacientes = clean_text_columns(normalize_columns(pacientes))
    internaciones = clean_text_columns(normalize_columns(internaciones))
    movimientos = clean_text_columns(normalize_columns(movimientos))

    pacientes = parse_dates(pacientes, ["FENAC"])
    internaciones = parse_dates(internaciones, ["FECHA_INGRESO", "FECHA_EGRESO"])
    movimientos = parse_dates(movimientos, ["FECHA_MOVIMIENTO"])

    return {
        "pacientes": pacientes,
        "internaciones": internaciones,
        "movimientos": movimientos,
    }
