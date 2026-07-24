# Inventario de datos

## Fuente

La fuente utilizada para este challenge es una base sintética creada en Google Sheets y exportada en formato CSV.

La estructura está inspirada en una base institucional migrada originalmente desde Microsoft Access, pero todos los registros son ficticios.

## Archivos incluidos

| Archivo | Categoría | Responsable | Uso en el agente |
|---|---|---|---|
| `pacientes.csv` | Pacientes sintéticos | Isabel Lorite | Identificar registros demo mediante `CHIST`. |
| `internaciones.csv` | Internaciones | Isabel Lorite | Analizar ingresos, egresos, diagnósticos y estados. |
| `movimientos.csv` | Movimientos | Isabel Lorite | Analizar ingresos, traslados, altas, derivaciones y pabellones. |

## Criterios de curaduría

- Se utilizan únicamente datos inventados.
- No se incluyen nombres, documentos, fechas ni registros reales.
- Se conservan relaciones lógicas entre tablas.
- Las claves principales permiten cruzar pacientes, internaciones y movimientos.
- Los CSV se almacenan en `data/raw` como fuente original del pipeline.

## Método de ingesta inicial

La ingesta inicial se realiza de forma manual:

```text
Google Sheets demo
   ↓
Exportación CSV
   ↓
Carpeta data/raw
   ↓
Procesamiento con Python y Pandas
```

## Permisos

El agente trabaja en modo lectura. No modifica los archivos originales.
