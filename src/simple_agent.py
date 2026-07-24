from src.data_loader import load_raw_data
from src.processor import enrich_data
from src.analysis_tools import answer_with_pandas


def answer_question(question: str) -> str:
    """Carga datos, procesa y responde una pregunta en lenguaje natural."""
    raw = load_raw_data()
    enriched = enrich_data(raw)
    data = {
        "pacientes": enriched["pacientes"],
        "internaciones": enriched["internaciones"],
        "movimientos": enriched["movimientos"],
    }
    return answer_with_pandas(question, data)
