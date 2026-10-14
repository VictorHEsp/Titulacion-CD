# Expansión de ECOBICI en la Ciudad de México
## Propuesta metodológica — versión 1.0

**Proyecto de titulación:** Licenciatura en Ciencia de Datos  

> **Propósito del documento.** Registrar los acuerdos iniciales sobre el problema, el alcance, las variables, las fuentes y el enfoque analítico. No representa resultados empíricos ni una metodología cerrada.

---

## 1. Contexto y planteamiento del problema

ECOBICI es un sistema de bicicletas compartidas cuya utilidad depende tanto de la demanda en los lugares donde se encuentran las estaciones como de la posibilidad de realizar trayectos entre múltiples puntos de una red. Una nueva estación puede atraer actividad, pero instalarla de manera aislada puede limitar su utilidad.

La expansión de ECOBICI plantea, por tanto, una decisión geográfica: **en qué zonas conviene incorporar nuevas estaciones** para atender una demanda potencial significativa y, simultáneamente, permitir que más habitantes de la Ciudad de México tengan acceso al sistema.

Este proyecto propone desarrollar una herramienta de apoyo a decisiones que combine análisis espacial, predicción de actividad de estaciones y evaluación de escenarios de expansión. **No busca sustituir los estudios de factibilidad operativa, presupuestal o de ingeniería vial** necesarios antes de instalar estaciones reales.

## 2. Pregunta de investigación

**¿Qué zonas de la Ciudad de México presentan mayor potencial para la expansión de ECOBICI si se busca equilibrar la actividad esperada de las nuevas estaciones y la cobertura poblacional adicional, considerando su relación con la red existente?**

### 2.1 Objetivo general

Desarrollar una metodología de Ciencia de Datos y un prototipo interactivo que permitan identificar y comparar zonas candidatas para expandir ECOBICI en la Ciudad de México, equilibrando demanda potencial y cobertura poblacional adicional, con consideraciones de conectividad de la red.

### 2.2 Objetivos específicos

1. Describir espacialmente la actividad de las estaciones actuales de ECOBICI y sus características de entorno.
2. Construir y evaluar modelos que estimen la **actividad diaria promedio** asociada con las características geográficas de estaciones existentes.
3. Generar una cuadrícula de zonas candidatas y estimar para cada una indicadores de potencial de uso y cobertura poblacional adicional.
4. Comparar combinaciones de zonas candidatas bajo distintos escenarios de expansión, tomando en cuenta la conectividad y evitando contar dos veces la cobertura superpuesta.
5. Implementar un tablero geográfico que permita explorar recomendaciones por alcaldía y entender sus fundamentos y limitaciones.

## 3. Alcance del proyecto

| Dimensión | Decisión preliminar |
|---|---|
| Zona de estudio | Ciudad de México; la visualización permitirá filtrar por alcaldía. |
| Datos históricos principales | Octubre de 2025 a septiembre de 2026 (12 meses completos, sujetos a control de calidad). |
| Unidad de observación para entrenamiento | Estación existente de ECOBICI. |
| Unidad geográfica de recomendación | Cuadrícula aproximada de **250 × 250 metros**. |
| Área de influencia inicial | **500 metros** alrededor de una ubicación; medida provisional a contrastar mediante sensibilidad. |
| Resultado analítico | Indicadores comparables de actividad potencial, población adicional cubierta y conectividad. |
| Resultado aplicado | Tablero interactivo de escenarios de expansión por alcaldía. |

**Distinción importante:** la cuadrícula de 250 × 250 m define dónde se evalúan zonas candidatas; los 500 m definen el entorno para calcular variables y la aproximación inicial a la cobertura. No son la misma escala.

El centroide de cada celda podría utilizarse como punto de referencia computacional, **no como coordenada definitiva de instalación**. De ser necesario, se restringirán las celdas a zonas geográficas elegibles antes de formular recomendaciones.

## 4. Objetivos analíticos y métricas

### 4.1 Variable objetivo del modelo predictivo

Para cada estación existente `i`, se utilizará inicialmente el **promedio diario de movimientos**:

\[
Y_i = \frac{I_i + F_i}{D_i}
\]

Donde:

- `I_i`: viajes que comenzaron en la estación `i` durante el periodo de estudio.
- `F_i`: viajes que terminaron en la estación `i` durante el periodo de estudio.
- `D_i`: número de días en los que la estación estuvo efectivamente operativa y es válida la observación; la forma de determinarlo dependerá de la disponibilidad de datos históricos de operación.

La métrica incorpora la función de la estación como punto de **salida y llegada**. **No es una cantidad de viajes únicos de toda la red:** un trayecto típico genera un movimiento de origen y uno de destino. Tampoco equivale automáticamente a *viajes nuevos netos* que surgirían al expandir el sistema.

**Pendientes de validación:** identificación consistente de estaciones a lo largo del tiempo; estaciones nuevas, retiradas o reubicadas; fechas de operación; valores anómalos; periodos de baja disponibilidad de bicicletas o anclajes. Si no se obtienen los días efectivos de operación, se documentará y evaluará una aproximación, sin asumir que cualquier día sin viajes equivale a un día operativo.

### 4.2 Cobertura poblacional adicional

Se pretende estimar cuántos habitantes que actualmente **no cuentan con una estación dentro del umbral de acceso definido** pasarían a estar cubiertos al agregar nuevas estaciones.

La cobertura marginal de un conjunto de nuevas ubicaciones debe considerar la **unión de las áreas cubiertas**, evitando contar doble a las personas que se encuentren dentro del alcance de más de una estación.

La estimación inicial utilizará distancias geográficas de 500 m; una medición por red peatonal sería una mejora potencial, sujeta al tiempo y a la disponibilidad de datos. La población provendrá de información censal y requerirá una asignación espacial cuidadosa a áreas de cobertura.

### 4.3 Conectividad de red

La conexión con estaciones existentes o con otras estaciones propuestas se utilizará como criterio de elegibilidad, restricción o evaluación de escenarios. Se definirán más adelante los umbrales apropiados, sin presuponer que existe un número universal de estaciones necesario para que una zona funcione.

## 5. Variables explicativas candidatas

Las variables se medirán alrededor de las estaciones existentes y, de forma análoga, alrededor de las ubicaciones candidatas. Las distancias deberán calcularse en un **sistema de coordenadas proyectadas en metros**, no directamente sobre grados de latitud/longitud.

| Grupo | Variable candidata | Operacionalización inicial | Fuente candidata | Prioridad |
|---|---|---|---|---|
| Demografía | Población cercana | Habitantes estimados dentro de 500 m | INEGI, Censo 2020 | Alta |
| Demografía | Densidad poblacional | Habitantes por km² en el entorno | INEGI, Censo 2020 | Alta |
| Actividad económica | Establecimientos cercanos | Conteo de unidades económicas dentro de 500 m | INEGI, DENUE | Alta |
| Actividad económica | Comercios y servicios | Conteo o proporción por grandes categorías | INEGI, DENUE | Media |
| Transporte público | Cercanía al Metro | Distancia a estación de Metro más próxima | Datos Abiertos CDMX | Alta |
| Transporte público | Cercanía al Metrobús | Distancia a estación de Metrobús más próxima | Datos Abiertos CDMX | Alta |
| Infraestructura ciclista | Cercanía a ciclovías | Distancia al tramo activo más próximo | SEMOVI / Datos Abiertos CDMX | Alta |
| Red ECOBICI | Densidad de estaciones | Número de estaciones actuales dentro de 500 m | ECOBICI | Alta |
| Red ECOBICI | Distancia a la red | Distancia a estación existente más cercana | ECOBICI | Alta |

**Consideración metodológica:** variables como la densidad de estaciones cercanas pueden cambiar si se proponen varias estaciones nuevas. Las variables de red se definirán de forma consistente con cada escenario y no se confundirán observaciones históricas con configuraciones hipotéticas futuras.

La capacidad de las estaciones se analizará como posible variable de control, siempre que pueda observarse y tratarse apropiadamente en zonas futuras; no se decidirá su inclusión automática antes de revisar los datos.

### Variables excluidas de la primera versión

No se modelarán explícitamente ingreso, equidad socioeconómica, seguridad vial, pendientes, tráfico vehicular, disponibilidad de espacio físico ni costos exactos de obra. Son factores potencialmente relevantes para decisiones reales y se reconocerán como límites del alcance, pero agregarlos ahora ampliaría demasiado el trabajo.

## 6. Fuentes de datos propuestas

| Fuente | Información esperada | Enlace | Verificación pendiente |
|---|---|---|---|
| ECOBICI — datos abiertos | CSV mensuales de viajes; información actual de estaciones mediante GBFS | https://ecobici.cdmx.gob.mx/datos-abiertos/ | Esquema, IDs, calidad y cambios históricos de estaciones. El feed GBFS es **actual**, no histórico. |
| INEGI — Censo de Población y Vivienda 2020 | Población a escala AGEB/manzana, según indicador y disponibilidad | https://www.inegi.org.mx/app/scitel/Default?ev=10 | Descargar geometrías compatibles y verificar variables disponibles. |
| INEGI — DENUE | Ubicación y actividad de establecimientos económicos | https://www.inegi.org.mx/app/mapa/denue/ | Versión y periodo de referencia; coordenadas y clasificación. |
| Datos Abiertos CDMX — Metro | Localización de estaciones de Metro | https://datos.cdmx.gob.mx/dataset/lineas-y-estaciones-del-metro | Vigencia y estaciones efectivamente operativas. |
| Datos Abiertos CDMX — Metrobús | Localización de estaciones de Metrobús | https://datos.cdmx.gob.mx/dataset/geolocalizacion-metrobus | Vigencia y estaciones efectivamente operativas. |
| Datos Abiertos CDMX — infraestructura vial ciclista | Geometrías de tramos ciclistas y estado | https://datos.cdmx.gob.mx/dataset/infraestructura-vial-ciclista | Filtrar tramos activos; revisar fecha y cobertura. |

**Nota de trazabilidad:** al descargar cada conjunto se registrarán fecha de acceso, versión, periodo de referencia, licencia, nombre de archivo y cualquier transformación realizada.

## 7. Metodología propuesta

### Fase 1. Obtención, limpieza e integración

1. Descargar los 12 archivos mensuales de viajes del periodo inicial.
2. Estandarizar formatos, fechas e identificadores de origen/destino; revisar viajes incompletos o inválidos.
3. Obtener el inventario de estaciones y comprobar la consistencia temporal de sus coordenadas e identificadores.
4. Incorporar datos censales, establecimientos, transporte público y ciclovías en un sistema geográfico común.
5. Construir una tabla reproducible a nivel de estación con la variable objetivo y los predictores disponibles.

### Fase 2. Análisis exploratorio

- Distribución de la actividad diaria por estación y diferencias entre zonas.
- Patrones temporales básicos: meses, días laborales y fines de semana, cuando sean útiles para explicar el dato agregado.
- Relaciones exploratorias entre actividad y características del entorno.
- Mapas de actividad, densidad de estaciones y cobertura actual.
- Revisión de sesgos, valores extremos, datos faltantes y cobertura espacial de la muestra.

### Fase 3. Modelado predictivo

Se contrastará al menos un **modelo base sencillo** con uno o más enfoques que aporten valor incremental. Entre los candidatos:

- **Baseline:** media global o una referencia simple que sirva para comparar modelos.
- **Regresión de Poisson:** candidato natural para conteos, evaluando supuestos, sobredispersión y tratamiento de exposición/días operativos.
- **Random Forest:** candidato flexible para patrones no lineales e interacciones.
- **XGBoost:** opción adicional únicamente si se justifica por mejora verificable frente a las alternativas anteriores.

Se evitará elegir una técnica solo por sofisticación. La decisión dependerá de la calidad y tamaño de los datos, el desempeño fuera de muestra y la interpretabilidad.

**Validación:** se utilizarán pruebas de desempeño con separación espacial entre estaciones (por ejemplo, bloques geográficos), además de métricas de error apropiadas como MAE y RMSE. Las transformaciones y selecciones de variables se ajustarán exclusivamente dentro de los datos de entrenamiento de cada partición. Se examinará el desempeño en zonas con características diferentes a las utilizadas para entrenar.

**Limitación esencial:** las estaciones existentes no constituyen una muestra aleatoria de toda la ciudad. El modelo predice actividad asociada a estaciones observadas bajo condiciones actuales; extrapolar a zonas nuevas implica incertidumbre y no prueba causalmente cuántos viajes *adicionales* producirá una instalación.

### Fase 4. Evaluación espacial de candidatas

1. Generar una cuadrícula de 250 × 250 m sobre el ámbito de estudio, usando una proyección en metros.
2. Identificar las celdas candidatas y excluir, si procede, zonas claramente no elegibles a partir de datos disponibles.
3. Calcular para cada celda los mismos predictores disponibles para estaciones existentes.
4. Estimar potencial de actividad, señalar incertidumbre y marcar celdas que estén fuera del rango de condiciones observadas en entrenamiento.
5. Estimar la población **adicional** a la que daría acceso una nueva estación representada por la celda.

### Fase 5. Selección y comparación de escenarios

Se partirá de la siguiente pregunta práctica: **si se incorporan `K` estaciones en determinada alcaldía, ¿qué conjunto de zonas candidatas ofrece el mejor equilibrio entre actividad esperada y cobertura adicional, respetando reglas básicas de conectividad?**

La primera versión podrá utilizar una selección iterativa transparente, que actualice la cobertura adicional al elegir cada zona. Después se evaluará, si está justificado, una optimización más formal.

No se fijarán todavía pesos definitivos para demanda y cobertura. Se podrán comparar distintos pesos o soluciones no dominadas para mostrar el intercambio entre objetivos. No se sumarán sin justificación las predicciones individuales como si fueran viajes nuevos independientes: puede existir sustitución de viajes, solapamiento de captación y cambios en la red.

**Fuera del MVP:** recomendar de forma automática el *número óptimo* de nuevas estaciones. Para hacerlo defensiblemente sería necesario definir un criterio adicional, como presupuesto, costo marginal, umbral de beneficio o meta de cobertura.

### Fase 6. Tablero interactivo

**Versión mínima viable (MVP):**

- Selección de alcaldía.
- Elección del número de estaciones a incorporar (`K`).
- Mapa con **cuadrículas recomendadas**, no coordenadas definitivas de obra.
- Indicadores de actividad potencial, cobertura poblacional adicional y conectividad.
- Comparación básica entre escenarios e información sobre supuestos y limitaciones.

**Extensiones posibles:** controles para ajustar la prioridad relativa de ambos objetivos, visualización de frontera de Pareto, recomendación automática de cantidad de estaciones condicionada a un presupuesto u otra regla explícita.

## 8. Evaluación de resultados

El proyecto se evaluará en dos niveles:

**Nivel predictivo:** desempeño fuera de muestra y bajo particiones espaciales; estabilidad de variables relevantes; sensibilidad a las decisiones de preprocesamiento.

**Nivel de recomendaciones:** cobertura poblacional incremental, potencial de actividad, conectividad y robustez de las zonas sugeridas ante cambios en el radio de acceso, tamaño de cuadrícula, pesos de objetivos y número de estaciones propuestas. Un tablero atractivo no sustituye evidencia analítica.

No se presentará una recomendación como una ubicación de instalación confirmada ni como un pronóstico causal de nuevos viajes sin evidencia adicional.

## 9. Limitaciones y riesgos conocidos

1. **Sesgo de selección:** las estaciones actuales se ubican en zonas previamente seleccionadas y pueden no representar territorios sin ECOBICI.
2. **Cambios temporales:** la red y los hábitos de movilidad cambian; los datos de diferentes fuentes corresponden a fechas distintas.
3. **Disponibilidad histórica:** la información actual de GBFS no equivale al historial de capacidad, ubicación y operación de cada estación.
4. **Demanda observada vs. latente:** la actividad realizada puede estar condicionada por disponibilidad de bicicletas/anclajes, no solo por interés de los usuarios.
5. **Cobertura aproximada:** un radio geométrico de 500 m no reproduce exactamente la distancia caminable real ni las barreras físicas.
6. **Distribución de población:** estimar habitantes dentro de radios a partir de polígonos censales supone decisiones de asignación espacial y conlleva incertidumbre.
7. **Interacción entre estaciones:** nuevas estaciones pueden redistribuir viajes existentes; la conectividad y el solapamiento importan.
8. **Viabilidad física y económica:** no se comprobarán individualmente permisos, obras, seguridad, espacio disponible ni costos reales de instalación.

## 10. Decisiones ya tomadas y decisiones abiertas

### Acuerdos establecidos

- Equilibrar **demanda potencial y cobertura poblacional**; no agregar equidad socioeconómica como objetivo explícito.
- Medir inicialmente la actividad histórica por estación mediante **inicios + llegadas por día operativo**.
- Estudiar toda la CDMX y permitir selección de alcaldía en el tablero.
- Utilizar **cuadrículas de 250 × 250 m**, en lugar de prometer lugares exactos.
- Comenzar con cinco familias de variables: demografía, actividad económica, transporte público, infraestructura ciclista y red ECOBICI.
- Tratar la conectividad de la red como aspecto a considerar en la recomendación.
- Empezar por un MVP que recomienda ubicaciones para un `K` indicado por el usuario.

### Pendientes por resolver con evidencia

- Cómo identificar correctamente días efectivos de operación y cambios históricos de estaciones.
- Procedimiento concreto para asignar población censal a zonas y radios de cobertura.
- Si el radio de 500 m es apropiado y qué tan sensibles son los resultados a él.
- Definición operacional de conectividad y elegibilidad de celdas.
- Selección final del algoritmo predictivo, según validación espacial.
- Método concreto para balancear objetivos y comparar escenarios.
- Qué restricciones adicionales se requerirían para determinar `K` automáticamente.

## 11. Plan inmediato de ejecución

| Etapa | Entregable |
|---|---|
| Descarga y auditoría de fuentes | Inventario real de archivos, diccionarios y consistencia temporal. |
| Dataset de estaciones y EDA | Tabla maestra por estación y mapas descriptivos. |
| Ingeniería de variables geográficas | Predictores espaciales reproducibles. |
| Modelos y evaluación | Baseline, alternativas justificadas y validación espacial. |
| Cuadrículas y selección de escenarios | Tabla de zonas candidatas y recomendaciones comparables. |
| Tablero y documentación | Prototipo funcional, metodología revisada y principales limitaciones. |

La secuencia es prioritaria; las fechas exactas se revisarán a medida que conozcamos la calidad y complejidad de las fuentes.

---

## Referencias iniciales a consultar

- ECOBICI, **Datos Abiertos**: https://ecobici.cdmx.gob.mx/datos-abiertos/
- INEGI, **Censo 2020 / SCITEL**: https://www.inegi.org.mx/app/scitel/Default?ev=10
- INEGI, **DENUE**: https://www.inegi.org.mx/app/mapa/denue/
- Gobierno de CDMX, **líneas y estaciones del Metro**: https://datos.cdmx.gob.mx/dataset/lineas-y-estaciones-del-metro
- Gobierno de CDMX, **geolocalización del Metrobús**: https://datos.cdmx.gob.mx/dataset/geolocalizacion-metrobus
- Gobierno de CDMX, **infraestructura vial ciclista**: https://datos.cdmx.gob.mx/dataset/infraestructura-vial-ciclista

*Documento de trabajo. Versión 1.0: las hipótesis y los métodos propuestos podrán revisarse a partir de la inspección y validación de datos.*
