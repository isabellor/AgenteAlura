import os
from pathlib import Path

import streamlit as st

from src.alura_agent_final import preguntar_agente
from src.rag_retriever import crear_indice


BASE_DIR = Path(__file__).resolve().parent
VECTOR_DIR = BASE_DIR / "data" / "vectorstore"
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# Permite usar secrets de Streamlit Cloud sin subir claves al repositorio.
try:
    if "OPENROUTER_API_KEY" in st.secrets and not os.environ.get("OPENROUTER_API_KEY"):
        os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
except Exception:
    pass


st.set_page_config(
    page_title="Consulta institucional demo",
    page_icon="🔎",
    layout="wide"
)


st.markdown(
    """
    <style>
        .main {
            background-color: #f7f8fa;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }

        .hero {
            padding: 2rem 2.2rem;
            border-radius: 22px;
            background: linear-gradient(135deg, #102033 0%, #1f3a5f 55%, #315f86 100%);
            color: white;
            margin-bottom: 1.4rem;
            box-shadow: 0 12px 32px rgba(16, 32, 51, 0.18);
        }

        .hero h1 {
            font-size: 2.35rem;
            margin-bottom: 0.6rem;
            line-height: 1.15;
        }

        .hero p {
            font-size: 1.05rem;
            line-height: 1.6;
            max-width: 840px;
            color: #e7eef7;
        }

        .pill-row {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 1.2rem;
        }

        .pill {
            padding: 0.36rem 0.75rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.22);
            color: #ffffff;
            font-size: 0.88rem;
        }

        .info-card {
            background: #ffffff;
            border: 1px solid #e6e9ef;
            border-radius: 18px;
            padding: 1.25rem 1.35rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
        }

        .info-card h3 {
            margin-top: 0;
            margin-bottom: 0.5rem;
            color: #162033;
        }

        .muted {
            color: #64748b;
            font-size: 0.94rem;
            line-height: 1.5;
        }

        .answer-card {
            background: #ffffff;
            border-left: 5px solid #315f86;
            border-radius: 16px;
            padding: 1.2rem 1.3rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.07);
            margin-top: 1rem;
        }

        .small-note {
            color: #64748b;
            font-size: 0.85rem;
        }

        div.stButton > button {
            border-radius: 999px;
            border: 1px solid #d7deea;
            padding: 0.45rem 0.9rem;
            background: #ffffff;
        }

        div.stButton > button:hover {
            border-color: #315f86;
            color: #315f86;
        }

        .stTextArea textarea {
            border-radius: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="hero">
        <h1>Consulta inteligente de registros institucionales</h1>
        <p>
            Asistente demo para explorar pacientes, internaciones y movimientos
            mediante preguntas en lenguaje natural. El sistema combina procesamiento
            de datos, recuperación semántica y herramientas de análisis.
        </p>
        <div class="pill-row">
            <span class="pill">CSV</span>
            <span class="pill">Pandas</span>
            <span class="pill">RAG</span>
            <span class="pill">Chroma</span>
            <span class="pill">LangChain</span>
            <span class="pill">Streamlit</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


with st.sidebar:
    st.markdown("## Agente Alura")
    st.markdown(
        """
        Aplicación demo desarrollada para consultar una base institucional
        mediante lenguaje natural.
        """
    )

    st.divider()

    st.markdown("### Componentes")
    st.markdown(
        """
        - Procesamiento con Pandas  
        - Documentos textuales  
        - Embeddings  
        - Índice vectorial Chroma  
        - Agente con herramientas  
        """
    )

    st.divider()

    st.markdown("### Alcance")
    st.caption(
        "Entorno de demostración. La base no contiene información real "
        "ni datos personales."
    )


col_info_1, col_info_2, col_info_3 = st.columns(3)

with col_info_1:
    st.markdown(
        """
        <div class="info-card">
            <h3>Datos</h3>
            <p class="muted">Pacientes, internaciones y movimientos organizados en archivos CSV.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_info_2:
    st.markdown(
        """
        <div class="info-card">
            <h3>Procesamiento</h3>
            <p class="muted">Limpieza, validación de relaciones y generación de registros enriquecidos.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_info_3:
    st.markdown(
        """
        <div class="info-card">
            <h3>Consulta</h3>
            <p class="muted">Respuestas en lenguaje natural combinando métricas y búsqueda semántica.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if not os.environ.get("OPENROUTER_API_KEY"):
    st.warning(
        "Falta configurar OPENROUTER_API_KEY. "
        "En Streamlit Cloud agregala desde Settings → Secrets."
    )


if not VECTOR_DIR.exists():
    st.info("Preparando el índice de búsqueda para la primera consulta...")
    try:
        mensaje = crear_indice(recrear=True)
        st.success(mensaje)
    except Exception as error:
        st.error(f"No se pudo crear el índice vectorial: {error}")


st.markdown("## Realizar una consulta")
st.markdown(
    """
    <p class="small-note">
    Podés preguntar por cantidades, diagnósticos, movimientos, pabellones,
    internaciones activas o buscar registros relacionados con un tema específico.
    </p>
    """,
    unsafe_allow_html=True
)


ejemplos = [
    "Dame un resumen ejecutivo de la base",
    "¿Cuántas internaciones activas hay?",
    "¿Qué diagnóstico aparece con mayor frecuencia?",
    "¿Qué pabellón tuvo más movimientos?",
    "¿Qué tipos de movimiento hay?",
    "Buscá registros relacionados con derivación",
    "Mostrame información sobre traslados entre pabellones",
    "Mostrame el historial del CHIST 100000",
]


with st.expander("Ver ejemplos de preguntas", expanded=True):
    cols = st.columns(2)

    for index, ejemplo in enumerate(ejemplos):
        with cols[index % 2]:
            if st.button(ejemplo, key=f"ejemplo_{index}"):
                st.session_state["pregunta_usuario"] = ejemplo


pregunta = st.text_area(
    "Escribí tu pregunta",
    key="pregunta_usuario",
    placeholder="Ejemplo: ¿Qué diagnóstico aparece con mayor frecuencia?",
    height=120
)


consultar = st.button("Consultar agente", type="primary")


if consultar:
    if not pregunta.strip():
        st.warning("Escribí una pregunta antes de consultar.")
    else:
        with st.spinner("Consultando registros y generando respuesta..."):
            try:
                respuesta = preguntar_agente(pregunta)

                st.markdown(
                    """
                    <div class="answer-card">
                        <h3>Respuesta</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(respuesta)

            except Exception as error:
                st.error(f"Ocurrió un error al consultar el agente: {error}")


st.divider()

st.caption(
    "Proyecto desarrollado para el Alura Agent Challenge. "
    "Base demo de consulta institucional con datos no reales."
)
