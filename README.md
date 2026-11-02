# Expansión de ECOBICI en la CDMX mediante predicción de actividad y optimización espacial

**Proyecto de titulación — Licenciatura en Ciencia de Datos, ITAM**  
**Autor:** Victor H. Esparza Díaz  
**Estado del proyecto:** análisis predictivo y optimización desarrollados; documentación, comparaciones de referencia, incertidumbre y publicación reproducible todavía en revisión (noviembre de 2026).

## ¿Qué problema resuelve?

El proyecto busca **priorizar cuadrículas de 250 × 250 m donde instalar `K` nuevas estaciones ECOBICI** en la Ciudad de México, equilibrando dos objetivos: (1) la actividad diaria potencial predicha y (2) la cobertura poblacional incremental, sin contar dos veces a los residentes cubiertos por varias estaciones. La selección considera restricciones geométricas de separación y conectividad.

La pregunta central es **dónde conviene ampliar la red dado un número `K` de estaciones y unas prioridades de cobertura y actividad**. El tablero interactivo es un medio para explorar los escenarios y presentar los resultados, no el objetivo de investigación. Las cuadrículas recomendadas **no son puntos definitivos de instalación**.

## Enfoque metodológico

1. **Datos y análisis espacial:** viajes ECOBICI de octubre de 2024 a septiembre de 2026 (24 meses), inventario de estaciones, población por manzana del Censo 2020, DENUE, infraestructura ciclista, Metro y Metrobús.
2. **Predicción:** entrenamiento sobre 670 estaciones con 12 meses de datos (octubre de 2025 a septiembre de 2026) y nueve variables urbanas. Se eligió **Random Forest** después de comparar alternativas mediante validación cruzada espacial.
3. **Candidatas:** 12,954 cuadrículas posibles de 250 × 250 m, caracterizadas mediante las mismas variables explicativas. La predicción se calcula una sola vez y permanece fija durante la selección.
4. **Selección multicriterio:** heurística iterativa de cobertura marginal y actividad predicha, con ponderaciones ajustables, separación mínima de 250 m y conectividad geométrica a 500 m. Se compara una expansión **exclusivamente conectada** con una alternativa **mixta** que admite núcleos independientes de al menos cinco estaciones.
5. **Presentación:** comparación de ubicaciones y escenarios con un tablero geográfico; se admite la selección de `K` y el filtro opcional por alcaldía.

## Resultados principales

Para **`K = 10`**, con coeficientes **65 % de cobertura y 35 % de actividad**:

| Indicador | Conectada (referencia) | Mixta (alternativa) |
|---|---:|---:|
| Cobertura poblacional incremental | 94,496 habitantes | 157,606 habitantes |
| Movimientos diarios predichos, suma de las 10 cuadrículas | 2,063.57 | 1,634.93 |
| Núcleos independientes de la red original | 0 | 2 (cinco estaciones cada uno) |
| Nuevas estaciones directamente próximas a la red original (≤ 500 m) | 2 | 0 |

La estrategia conectada es el **escenario de referencia** por mantener una unión geométrica con la red existente, directamente o mediante otras estaciones nuevas. La mixta amplía más la cobertura, pero sus dos núcleos requieren una evaluación operativa adicional. **Ninguna estrategia es universalmente superior**: las diferencias cambian con las ponderaciones y las reglas de selección.

El modelo Random Forest obtuvo un **MAE espacial de 56.67 movimientos diarios por estación**, frente a **70.69** de una referencia que predice la mediana de entrenamiento (mejora relativa de **19.83 %**). La correlación global de Spearman entre valores observados y predicciones fuera de muestra fue **0.623**. Estos resultados corresponden a estaciones existentes; **no validan directamente las predicciones de las cuadrículas nuevas**.

## Límites de interpretación

- **Movimientos no equivale a viajes nuevos netos:** la variable es retiros más arribos diarios. No se descuentan viajes que podrían redistribuirse desde otras estaciones.
- **Extrapolación espacial:** el 93.73 % de las candidatas tiene un número de estaciones ECOBICI cercanas fuera del rango observado durante el entrenamiento (12,141 tienen cero); no hay actividad real observada para validar estas ubicaciones.
- **Conectividad aproximada:** 500 m es distancia euclidiana, no una ruta vial, peatonal ni ciclista comprobada.
- **Optimización heurística:** las recomendaciones son aproximadas; no existe garantía de óptimo global.
- **Factibilidad:** no se incorporan costos de obra, espacio físico, seguridad vial integral, capacidad/redistribución de bicicletas ni permisos.

## Archivos y flujo de análisis

Los notebooks disponibles para el análisis incluyen:

- `EDA_v1.ipynb` a `EDA_v6.ipynb`: preparación y análisis exploratorio de las fuentes.
- `Modelado_v1.ipynb`: comparación de modelos, validación espacial, importancia de variables y análisis de errores.
- `Variables_v1_Candidatas.ipynb`: construcción de variables de cuadrículas, predicción de actividad y análisis de extrapolación.
- `Optimizacion_v1.ipynb`: cobertura incremental, grafo geométrico, heurística, sensibilidad y exportación para el tablero.
- `motor_ecobici.py`: motor de selección utilizado por el prototipo, referido desde el notebook de optimización.
- `metodologia.md`: descripción detallada de variables, reglas, métricas, resultados y limitaciones.

**Rutas importantes:** los notebooks consultados usan rutas relativas como `../Data/Procesados/datos_modelo_ECOBICI.csv`, `../Data/Procesados/variables_candidatas_ECOBICI.gpkg` y `../Data/Procesados/Tablero/`. Respeta las mayúsculas de `Data` y la ubicación relativa de los notebooks. **No se ha verificado que todos esos datos estén incluidos en el repositorio público**.

## Reproducción y tablero

El flujo analítico se organiza como preparación de datos → modelado y variables de candidatas → optimización → exportación de insumos al tablero. El notebook de optimización contiene una exportación de archivos geoespaciales y matrices al directorio `Data/Procesados/Tablero/`.

**Estado de reproducibilidad:** todavía está pendiente publicar y comprobar un procedimiento completo de instalación y ejecución desde un repositorio limpio (dependencias fijadas, disponibilidad de datos o mecanismo de descarga, instrucciones de arranque, Docker y acceso público al tablero). Por esta razón, este README **no presenta comandos de ejecución como si ya estuvieran verificados**. La ejecución local requiere preparar las dependencias geoespaciales y los archivos de datos indicados por los notebooks.

## Trabajo pendiente

- Comparación con portafolios de referencia e intervalos de incertidumbre para la actividad total de las recomendaciones.
- Revisión de mapas, figuras y consistencia de resultados del informe.
- Completar los archivos e instrucciones de reproducción y facilitar el acceso al tablero.
- Como validación futura: evaluar ubicaciones inauguradas después del entrenamiento o un piloto real para medir la capacidad de generalización fuera de la red actual.

Para detalles metodológicos y advertencias, consulta `metodologia.md` (o `docs/metodologia.md`, según su ubicación en el repositorio).
