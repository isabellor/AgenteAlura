
import re
from pathlib import Path

import pandas as pd

from langchain_core.tools import tool
from langchain_openrouter import ChatOpenRouter
from langgraph.prebuilt import create_react_agent

from src.rag_retriever import recuperar_contexto


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def cargar_datos():
    pacientes = pd.read_csv(PROCESSED_DIR / "pacientes_procesados.csv")
    internaciones = pd.read_csv(PROCESSED_DIR / "internaciones_procesadas.csv")
    movimientos = pd.read_csv(PROCESSED_DIR / "movimientos_enriquecidos.csv")
    return pacientes, internaciones, movimientos


@tool
def resumen_base(consulta: str = "") -> str:
    """
    Devuelve un resumen general del dataset institucional sintético.
    """
    pacientes, internaciones, movimientos = cargar_datos()

    total_pacientes = len(pacientes)
    total_internaciones = len(internaciones)
    total_movimientos = len(movimientos)

    if "FECHA_EGRESO" in internaciones.columns:
        internaciones_activas = internaciones["FECHA_EGRESO"].isna().sum()
    else:
        internaciones_activas = 0

    return (
        "Resumen del dataset sintético:\n"
        f"- Pacientes: {total_pacientes}\n"
        f"- Internaciones: {total_internaciones}\n"
        f"- Movimientos: {total_movimientos}\n"
        f"- Internaciones activas: {internaciones_activas}"
    )


@tool
def contar_internaciones_activas(consulta: str = "") -> str:
    """
    Cuenta cuántas internaciones activas hay.
    """
    _, internaciones, _ = cargar_datos()

    if "FECHA_EGRESO" not in internaciones.columns:
        return "No se encontró la columna FECHA_EGRESO."

    cantidad = internaciones["FECHA_EGRESO"].isna().sum()

    return f"Hay {cantidad} internaciones activas en el dataset sintético."


@tool
def diagnosticos_frecuentes(consulta: str = "") -> str:
    """
    Devuelve los diagnósticos más frecuentes de las internaciones.
    """
    _, internaciones, _ = cargar_datos()

    if "DIAGNOSTICO" not in internaciones.columns:
        return "No se encontró la columna DIAGNOSTICO."

    conteo = internaciones["DIAGNOSTICO"].value_counts().head(10)

    respuesta = "Diagnósticos más frecuentes:\n"
    for diagnostico, cantidad in conteo.items():
        respuesta += f"- {diagnostico}: {cantidad}\n"

    return respuesta


@tool
def movimientos_por_pabellon(consulta: str = "") -> str:
    """
    Devuelve los pabellones con mayor cantidad de movimientos registrados.
    """
    _, _, movimientos = cargar_datos()

    if "PABELLON" not in movimientos.columns:
        return "No se encontró la columna PABELLON."

    conteo = movimientos["PABELLON"].value_counts().head(10)

    respuesta = "Pabellones con más movimientos:\n"
    for pabellon, cantidad in conteo.items():
        respuesta += f"- {pabellon}: {cantidad}\n"

    return respuesta


@tool
def tipos_de_movimiento(consulta: str = "") -> str:
    """
    Devuelve la cantidad de registros por tipo de movimiento.
    """
    _, _, movimientos = cargar_datos()

    if "TIPO_MOVIMIENTO" not in movimientos.columns:
        return "No se encontró la columna TIPO_MOVIMIENTO."

    conteo = movimientos["TIPO_MOVIMIENTO"].value_counts()

    respuesta = "Tipos de movimiento registrados:\n"
    for tipo, cantidad in conteo.items():
        respuesta += f"- {tipo}: {cantidad}\n"

    return respuesta


@tool
def historial_por_chist(consulta: str) -> str:
    """
    Busca el historial de movimientos de una paciente a partir de su CHIST.
    """
    _, _, movimientos = cargar_datos()

    if "CHIST" not in movimientos.columns:
        return "No se encontró la columna CHIST en la tabla enriquecida."

    numeros = re.findall(r"\d+", consulta)

    if not numeros:
        return "No se encontró ningún número de CHIST en la consulta."

    chist = numeros[0]

    datos = movimientos[
        movimientos["CHIST"].astype(str) == chist
    ]

    if datos.empty:
        return f"No se encontraron movimientos para el CHIST {chist}."

    columnas_posibles = [
        "ID_INTERNACION",
        "FECHA_MOVIMIENTO",
        "TIPO_MOVIMIENTO",
        "PABELLON",
        "DIAGNOSTICO",
        "ESTADO_INTERNACION"
    ]

    columnas = [col for col in columnas_posibles if col in datos.columns]

    respuesta = f"Historial encontrado para CHIST {chist}:\n"

    for _, fila in datos[columnas].iterrows():
        detalle = " | ".join(
            f"{col}: {fila[col]}" for col in columnas
        )
        respuesta += f"- {detalle}\n"

    return respuesta


@tool
def buscar_en_documentos(consulta: str) -> str:
    """
    Usa la base vectorial para recuperar fragmentos relevantes del dataset.
    Esta herramienta sirve para preguntas abiertas, búsqueda semántica,
    registros relacionados con altas, traslados, derivaciones, observaciones o historiales.
    """
    return recuperar_contexto(consulta, k=5)


def crear_agente():
    llm = ChatOpenRouter(
        model="openai/gpt-4o-mini",
        temperature=0
    )

    herramientas = [
        resumen_base,
        contar_internaciones_activas,
        diagnosticos_frecuentes,
        movimientos_por_pabellon,
        tipos_de_movimiento,
        historial_por_chist,
        buscar_en_documentos
    ]

    prompt = """
    Eres un agente de IA para consultar una base institucional sintética.

    La base tiene tres tablas:
    - Pacientes
    - Internaciones
    - Movimientos

    Todos los datos son ficticios y se usan con fines educativos.

    Reglas:
    - Responde en español claro.
    - Usa herramientas para consultar el dataset.
    - No inventes cifras.
    - Para cantidades, rankings y métricas, usa herramientas basadas en Pandas.
    - Para preguntas abiertas o de búsqueda textual, usa la herramienta buscar_en_documentos.
    - Si usas fragmentos recuperados, resume la información y menciona que la respuesta se basa en fragmentos del índice vectorial.
    """

    return create_react_agent(
        model=llm,
        tools=herramientas,
        prompt=prompt
    )


def preguntar_agente(pregunta: str) -> str:
    agente = crear_agente()

    resultado = agente.invoke(
        {
            "messages": [
                ("user", pregunta)
            ]
        }
    )

    return resultado["messages"][-1].content
