
import os
from pathlib import Path

import streamlit as st

from src.alura_agent_final import preguntar_agente
from src.rag_retriever import crear_indice


BASE_DIR = Path(__file__).resolve().parent
VECTOR_DIR = BASE_DIR / "data" / "vectorstore"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


st.set_page_config(
    page_title="Alura Agent Challenge",
    page_icon="🤖",
    layout="centered"
)


st.title("Alura Agent Challenge")
st.subheader("Consulta inteligente de una base institucional sintética")

st.markdown(
    """
    Esta aplicación permite hacer preguntas en lenguaje natural sobre una base
    institucional sintética compuesta por pacientes, internaciones y movimientos.

    Los datos utilizados son ficticios y se usan únicamente con fines educativos.
    """
)


with st.expander("Ejemplos de preguntas"):
    st.markdown(
        """
        - Dame un resumen ejecutivo de la base
        - ¿Cuántas internaciones activas hay?
        - ¿Qué diagnóstico aparece con mayor frecuencia?
        - ¿Qué pabellón tuvo más movimientos?
        - ¿Qué tipos de movimiento hay?
        - Buscá registros relacionados con derivación
        - Mostrame información sobre traslados entre pabellones
        - Mostrame el historial del CHIST 100000
        """
    )


if not os.environ.get("OPENROUTER_API_KEY"):
    st.warning(
        "No se encontró la variable OPENROUTER_API_KEY. "
        "Configurala antes de usar el agente."
    )


if not VECTOR_DIR.exists():
    st.info("No se encontró el índice vectorial. Creándolo automáticamente...")
    try:
        mensaje = crear_indice(recrear=True)
        st.success(mensaje)
    except Exception as error:
        st.error(f"No se pudo crear el índice vectorial: {error}")


pregunta = st.text_area(
    "Escribí tu pregunta",
    placeholder="Ejemplo: ¿Qué diagnóstico aparece con mayor frecuencia?"
)


consultar = st.button("Consultar agente")


if consultar:
    if not pregunta.strip():
        st.warning("Escribí una pregunta antes de consultar.")
    else:
        with st.spinner("Consultando el agente..."):
            try:
                respuesta = preguntar_agente(pregunta)
                st.markdown("### Respuesta")
                st.write(respuesta)
            except Exception as error:
                st.error(f"Ocurrió un error al consultar el agente: {error}")


st.divider()

st.caption(
    "Proyecto educativo desarrollado para el Alura Agent Challenge. "
    "Dataset sintético basado en archivos CSV."
)
