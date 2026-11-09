# Fuentes originales de datos — ECOBICI CDMX

Este inventario documenta las fuentes utilizadas para preparar los datos del proyecto. **Los datos originales no se distribuyen en el repositorio** por su volumen. Las rutas de la columna «Archivo local» corresponden a la estructura de trabajo del autor y **no** implican que los archivos se encuentren en GitHub.

> **Pendiente de completar:** las fechas exactas de descarga y, donde se indique, el enlace específico de descarga. No deben confundirse con las fechas de consulta de las referencias bibliográficas.

| Fuente | Datos utilizados | Archivo local o patrón | Fuente de consulta / descarga | Fecha de descarga |
|---|---|---|---|---|
| ECOBICI, datos abiertos | Viajes mensuales de octubre de 2024 a septiembre de 2026 (24 CSV) | `data/Viajes_ECOBICI/YYYY-MM.csv` | https://ecobici.cdmx.gob.mx/datos-abiertos/ | 3 de octubre del 2026 |
| ECOBICI, catálogo de estaciones | ID y ubicación de las estaciones | `data/Estaciones_ECOBICI/estaciones_ECOBICI.csv` | -  | 3 de octubre del 2026 |
| INEGI, Censo de Población y Vivienda 2020 | Indicadores poblacionales y geografía de manzanas | `data/INEGI/AGEB.csv`; `data/INEGI/poligonos.json` | https://www.inegi.org.mx/programas/ccpv/2020/ | 3 de octubre del 2026 |
| INEGI, DENUE | Establecimientos y variables de actividad económica | `data/INEGI/denue_inegi_09_.csv` | https://www.inegi.org.mx/app/mapa/denue/ | | 3 de octubre del 2026 |
| SEMOVI / Datos Abiertos CDMX | Infraestructura ciclista | `data/Info_infra_ciclista/infra_vial_ciclista.json`; `data/Info_infra_ciclista/infraestructura_vial_ciclista/` | https://datos.cdmx.gob.mx/dataset/infraestructura-vial-ciclista | 3 de octubre del 2026 |
| STC Metro / Datos Abiertos CDMX | Estaciones y líneas del Metro | `data/Info_transporte/stcmetro_shp/` | https://datos.cdmx.gob.mx/dataset/lineas-y-estaciones-del-metro | 3 de octubre del 2026 |
| Metrobús / Datos Abiertos CDMX | Estaciones de Metrobús | `data/Info_transporte/mb_shp/` | https://datos.cdmx.gob.mx/dataset/geolocalizacion-metrobus | 3 de octubre del 2026 |
| Geografía de alcaldías, CDMX | Límites de alcaldías | `data/Info_geo/alcaldias.json` | - | 3 de octubre del 2026 |

## Reproducción

La ejecución rápida documentada en el README principal utilizará archivos intermedios versionados en `data/processed/`, sin requerir descargar todos los viajes originales. Para rehacer la preparación desde los datos originales, se deben descargar las fuentes correspondientes y conservar los nombres y rutas esperados por los notebooks.

Los *shapefiles* requieren todos sus archivos asociados (por ejemplo, `.shp`, `.shx`, `.dbf` y `.prj`), no solamente el archivo `.shp`.

**Criterio temporal del análisis:** viajes de octubre de 2024 a septiembre de 2026; para el modelado se utiliza octubre de 2025 a septiembre de 2026.
