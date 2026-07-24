
import json
import shutil
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
VECTOR_DIR = BASE_DIR / "data" / "vectorstore"

DOCUMENTOS_PATH = PROCESSED_DIR / "documentos_movimientos.jsonl"

NOMBRE_COLECCION = "movimientos_moyano_demo"
MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def cargar_documentos():
    """
    Carga los documentos generados durante el procesamiento.
    Cada línea del JSONL representa un fragmento textual con metadatos.
    """
    documentos = []
    metadatos = []
    ids = []

    with open(DOCUMENTOS_PATH, "r", encoding="utf-8") as archivo:
        for indice, linea in enumerate(archivo):
            registro = json.loads(linea)

            texto = (
                registro.get("page_content")
                or registro.get("text")
                or registro.get("contenido")
                or str(registro)
            )

            metadata = registro.get("metadata", {})

            documentos.append(texto)
            metadatos.append(metadata)
            ids.append(f"doc_{indice}")

    return ids, documentos, metadatos


def crear_indice(recrear=False):
    """
    Crea una base vectorial persistente con Chroma.
    Convierte cada documento en embedding y lo guarda junto con sus metadatos.
    """
    if recrear and VECTOR_DIR.exists():
        shutil.rmtree(VECTOR_DIR)

    VECTOR_DIR.mkdir(parents=True, exist_ok=True)

    cliente = chromadb.PersistentClient(path=str(VECTOR_DIR))

    coleccion = cliente.get_or_create_collection(
        name=NOMBRE_COLECCION,
        metadata={"hnsw:space": "cosine"}
    )

    ids, documentos, metadatos = cargar_documentos()

    if coleccion.count() > 0 and not recrear:
        return f"El índice ya existe con {coleccion.count()} documentos."

    modelo = SentenceTransformer(MODELO_EMBEDDINGS)

    embeddings = modelo.encode(
        documentos,
        normalize_embeddings=True
    ).tolist()

    coleccion.add(
        ids=ids,
        documents=documentos,
        metadatas=metadatos,
        embeddings=embeddings
    )

    return f"Índice creado con {coleccion.count()} documentos."


def recuperar_contexto(pregunta, k=5):
    """
    Transforma la pregunta en embedding y recupera los fragmentos más cercanos.
    Devuelve texto ensamblado con contenido y metadatos.
    """
    cliente = chromadb.PersistentClient(path=str(VECTOR_DIR))

    coleccion = cliente.get_collection(
        name=NOMBRE_COLECCION
    )

    modelo = SentenceTransformer(MODELO_EMBEDDINGS)

    embedding_pregunta = modelo.encode(
        [pregunta],
        normalize_embeddings=True
    ).tolist()[0]

    resultados = coleccion.query(
        query_embeddings=[embedding_pregunta],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    documentos = resultados["documents"][0]
    metadatos = resultados["metadatas"][0]
    distancias = resultados["distances"][0]

    contexto = []

    for i, documento in enumerate(documentos):
        metadata = metadatos[i]
        distancia = round(distancias[i], 4)

        bloque = (
            f"Fragmento {i + 1}\n"
            f"Distancia semántica: {distancia}\n"
            f"Metadatos: {metadata}\n"
            f"Contenido:\n{documento}"
        )

        contexto.append(bloque)

    return "\n\n---\n\n".join(contexto)
