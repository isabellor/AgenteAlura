import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.data_loader import load_raw_data
from src.processor import validate_relationships, enrich_data, save_processed_data
from src.text_builder import build_movement_documents, save_documents_jsonl


def main():
    print("Cargando CSV...")
    raw = load_raw_data()

    print("Validando relaciones...")
    validation = validate_relationships(raw)
    for key, value in validation.items():
        print(f"{key}: {value}")

    print("Generando tablas enriquecidas...")
    enriched = enrich_data(raw)
    save_processed_data(enriched)

    print("Creando documentos estructurados...")
    documents = build_movement_documents(enriched["movimientos_enriquecidos"])
    save_documents_jsonl(documents)

    print("Procesamiento finalizado.")
    print("Archivos generados en data/processed/")


if __name__ == "__main__":
    main()
