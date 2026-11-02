# Expansión de ECOBICI en la Ciudad de México
## Metodología implementada, evaluación y limitaciones

**Proyecto de titulación:** Licenciatura en Ciencia de Datos, ITAM  
**Corte de documentación:** noviembre de 2026  
**Alcance:** documenta el análisis y la optimización desarrollados. No equivale a una validación operativa de nuevas estaciones ni garantiza la reproducción integral del repositorio desde cero.

---

## 1. Contexto y planteamiento del problema

ECOBICI constituye una alternativa de movilidad para desplazamientos urbanos. Su expansión enfrenta un intercambio: las zonas que podrían registrar mayor actividad no necesariamente coinciden con aquellas donde puede cubrirse a más habitantes que actualmente no tienen una estación cercana. También importa la relación entre estaciones nuevas y existentes.

Este trabajo busca **identificar zonas de expansión prioritarias** bajo un número fijo de estaciones nuevas, equilibrando la actividad potencial **predicha** y la cobertura poblacional incremental, con reglas explícitas de conectividad. Se trata de un instrumento cuantitativo de apoyo a la planeación; la decisión final requiere evaluación física y operativa.

## 2. Pregunta y objetivos

**Pregunta de investigación:** ¿En qué cuadrículas de 250 × 250 metros de la Ciudad de México conviene instalar `K` nuevas estaciones ECOBICI para equilibrar la actividad potencial predicha y la cobertura poblacional incremental, considerando restricciones de conectividad?

**Objetivo general:** determinar conjuntos de zonas candidatas para ampliar ECOBICI, dadas las prioridades de cobertura y actividad, mediante predicción y selección espacial multicriterio.

**Objetivos específicos:**

1. Describir la actividad observada de las estaciones y su relación con las características urbanas.
2. Evaluar modelos para predecir los movimientos diarios de estaciones usando validación espacial.
3. Caracterizar cuadrículas candidatas de 250 × 250 m y reconocer sus diferencias respecto a las estaciones observadas.
4. Seleccionar `K` cuadrículas considerando cobertura adicional, actividad predicha y conectividad, y analizar la sensibilidad a los parámetros.
5. Comunicar los escenarios mediante un tablero interactivo, como **medio de consulta de resultados**, no como objetivo sustantivo de investigación.

El posible usuario institucional de la evidencia es la autoridad responsable de planear la expansión, como SEMOVI; los coeficientes y el número de nuevas estaciones representan decisiones de planeación.

## 3. Alcance y unidades de análisis

| Aspecto | Implementación o decisión |
|---|---|
| Región | Ciudad de México; filtro opcional por alcaldía (sin filtro: CDMX completa). |
| Periodo histórico | Octubre de 2024–septiembre de 2026 (24 meses). |
| Periodo para la variable objetivo | Octubre de 2025–septiembre de 2026 (365 días). |
| Estaciones del catálogo | 677 identificadores; 670 estaciones con información suficiente para el modelo. |
| Unidad del modelo predictivo | Una estación existente. |
| Unidad de recomendación | Una cuadrícula de 250 × 250 m, representada analíticamente por su centroide. |
| Candidatas | 12,954 cuadrículas después de excluir las ocupadas por estaciones. |
| Número de nuevas estaciones | `K`, definido por el usuario; en los escenarios reportados, `K = 10`. La implementación documentada utiliza `K ≥ 10`. |
| Distancias | Sistema proyectado EPSG:32614; 250 m de separación mínima y 500 m como umbral geométrico de conexión y cobertura. |

**Diferencia de escalas:** la celda de 250 m delimita una **zona candidata**; el radio de 500 m aproxima su cobertura y la posible conexión entre estaciones. Ninguna celda fija una coordenada de obra.

## 4. Datos, integración y variable objetivo

### 4.1 Fuentes

- **ECOBICI, datos abiertos:** registros de viajes e inventario de estaciones. Se procesaron **39,690,611 registros** del periodo histórico de 24 meses.
- **INEGI, Censo de Población y Vivienda 2020:** población por manzana urbana; se utilizaron **66,449 manzanas** tras la depuración.
- **INEGI, DENUE:** **460,762 establecimientos** georreferenciados para indicadores de actividad económica.
- **SEMOVI / datos abiertos de la CDMX:** infraestructura ciclista (inventario referido a marzo de 2025), estaciones del Metro y del Metrobús.

Estas fuentes **no corresponden todas al mismo año**. Se utilizan como aproximaciones al entorno urbano del periodo analizado; sus diferencias temporales son una limitación.

### 4.2 Movimientos diarios observados

Para cada estación `i`, la variable objetivo usada en el entrenamiento es:

$$
Y_i = \frac{R_i + A_i}{365}
$$

Donde `R_i` representa los retiros y `A_i` los arribos registrados entre octubre de 2025 y septiembre de 2026. Se seleccionaron las 670 estaciones con información suficiente para ese periodo; otras siete quedaron fuera del conjunto predictivo.

**Aclaración frente a la propuesta inicial:** el análisis implementado divide entre **365 días calendario**, no entre días efectivos de operación. Esto permite comparaciones uniformes, pero no corrige cierres, interrupciones ni posibles restricciones por falta de bicicletas o anclajes. La actividad observada no equivale a demanda latente y sumar retiros más arribos **no** equivale a contar viajes únicos o viajes netos adicionales.

### 4.3 Nueve variables explicativas

| Variable en los datos | Interpretación |
|---|---|
| `poblacion_500m` | Habitantes en un radio de 500 m. |
| `negocios_500m` | Establecimientos DENUE a 500 m. |
| `personal_500m` | Personal ocupado aproximado en establecimientos a 500 m. |
| `dist_metro` | Distancia al Metro más cercano. |
| `dist_metrobus` | Distancia al Metrobús más cercano. |
| `infra_ciclista_500m` | Longitud de infraestructura ciclista dentro de 500 m. |
| `estaciones_ecobici_500m` | Número de estaciones ECOBICI existentes a 500 m. |
| `universidades_500m` | Establecimientos de educación superior a 500 m. |
| `dist_centro` | Distancia al Zócalo. |

Las mismas nueve características se calculan para los centroides de las cuadrículas candidatas. Los valores de `estaciones_ecobici_500m` en candidatas se calculan **con la red preexistente**, no con las estaciones propuestas en cada escenario.

## 5. Cobertura poblacional y candidatas

Se toma un punto representativo interior de cada manzana para asociarle su población censal. Se considera cubierta si ese punto se encuentra a **500 m o menos en línea recta** de alguna estación. La cobertura se calcula sobre la **unión** de áreas, sin duplicar habitantes alcanzados por varias estaciones.

Con el catálogo de **677 estaciones**, la población estimada inicialmente cubierta es **1,167,905 personas**, equivalente al **12.77 %** de la población incorporada al análisis. Se construyeron **13,543** cuadrículas urbanas de 250 × 250 m; se retiraron **589** que contenían estaciones existentes, con **12,954 candidatas** restantes.

Para cada candidata se construyó una matriz de qué manzanas no cubiertas podría incorporar. Durante la selección, la población disponible se actualiza después de cada decisión, de modo que el beneficio de cobertura se calcula **marginalmente**.

La cobertura es una **aproximación residencial**, no una medida de accesibilidad peatonal real, utilización ni equidad socioeconómica.

## 6. Modelado predictivo y validación

Se compararon la predicción constante de la mediana, regresión lineal, Ridge, Random Forest, Gradient Boosting, XGBoost y Ridge polinómica. El modelo seleccionado para estimar actividad en candidatas fue **Random Forest**, con **300 árboles**, **mínimo de 3 observaciones por hoja** y **semilla 42**.

### 6.1 Evaluación espacial

Se aplicó **GroupKFold de cinco particiones**, agrupando las 670 estaciones en **28 bloques geográficos de 2 × 2 km**. Las métricas corresponden a predicciones de estaciones no utilizadas en el entrenamiento de su partición.

| Métrica | Resultado |
|---|---:|
| MAE de referencia (mediana del entrenamiento) | 70.69 movimientos diarios |
| MAE de Random Forest | **56.67 movimientos diarios** |
| Reducción relativa del MAE frente a la referencia | **19.83 %** |
| Actividad media observada en las 670 estaciones | 151.77 movimientos diarios |
| Spearman global, real frente a predicho | **0.623** |
| WAPE global | **37.33 %** |
| Precision@10 %: estaciones del decil de mayor actividad identificadas | **21 de 67 (31.34 %)** |

La mejora frente a la referencia **no fue uniforme entre particiones**; en una de ellas el Random Forest obtuvo un MAE ligeramente superior al de la mediana. En el decil más activo, el MAE aumentó a **156.02** y la actividad media se subestimó (368.55 observados frente a 213.01 predichos). Spearman por partición varió entre **0.359 y 0.744**.

Ridge polinómica alcanzó MAE **56.15** mediante búsqueda **anidada** de parámetros, mientras que el 56.67 de Random Forest corresponde a la **configuración fija**; por tanto, no son evaluaciones estrictamente equivalentes. Al aplicar Ridge polinómica a candidatas aparecieron **801 valores negativos** y predicciones por encima de **14,301 movimientos diarios**. Se eligió Random Forest por su desempeño competitivo y por producir predicciones numéricamente más plausibles, **sin considerar esto una prueba de exactitud fuera de la red**.

### 6.2 Robustez y dependencia de variables

- Al excluir del entrenamiento estaciones a 500 m o menos de las de evaluación, el MAE de Random Forest pasó de **56.67 a 62.10** (referencia en este ejercicio: **71.28**). La prueba también reduce el tamaño de entrenamiento y no aísla únicamente la dependencia espacial.
- Al emplear bloques de **1, 2 y 4 km**, los MAE medios fueron **54.71**, **56.67** y **56.83**; la variación entre particiones fue mayor para 4 km.
- La **distancia al Zócalo** fue la variable más influyente en la evaluación por permutación; sin ella, el MAE pasó de **56.67 a 61.18**.
- **No existe** un conjunto de prueba independiente de la validación cruzada ni valores observados de actividad en las nuevas cuadrículas propuestas.

### 6.3 Aplicabilidad fuera de la red

| Variable | Candidatas fuera del rango de entrenamiento |
|---|---:|
| Estaciones ECOBICI a 500 m | 12,142 (93.73 %) |
| Distancia al Zócalo | 8,264 (63.79 %) |
| Distancia al Metro | 7,035 (54.31 %) |
| Distancia al Metrobús | 5,400 (41.69 %) |

En la primera fila, **12,141** candidatas tienen cero estaciones existentes a 500 m (por debajo del mínimo de entrenamiento, que es uno) y **una** supera el máximo observado.

La actividad media **predicha** pasa de **124.29 movimientos diarios** para candidatas a 500 m o menos de la red a **95.40** para aquellas a 2–5 km y **89.29** a más de 5 km. En validación sobre estaciones existentes, el modelo subestimó en promedio **7.37** movimientos diarios en el cuartil más céntrico y sobreestimó **12.75** en el cuartil más alejado del Zócalo (sesgo definido como real menos predicho).

Estos resultados describen limitaciones de extrapolación; **no demuestran** cuál será el error ni si el modelo ordenará correctamente cuadrículas donde ECOBICI todavía no opera.

## 7. Selección espacial y función objetivo

Se buscan `K` cuadrículas bajo reglas de distancia, conectividad y, opcionalmente, un filtro por alcaldía. La función multicriterio conceptual es:

$$
\max_{S\in\mathcal F,\,|S|=K} F(S)
= w_p\frac{\operatorname{Pob}(S)}{E_p}
+ w_d\frac{\sum_{j\in S} D_j}{E_d},
\qquad w_p+w_d=1
$$

Donde `S` es el conjunto seleccionado, `Pob(S)` es la cobertura **incremental** respecto a la red actual y sin doble conteo, `D_j` la actividad diaria predicha para la cuadrícula `j`, y `\mathcal F` el conjunto de portafolios que cumplen las reglas. En la implementación se utilizaron como escalas de normalización los **percentiles 95 de candidatas elegibles**, `E_p ≈ 18,798.05` habitantes y `E_d ≈ 128.46` movimientos diarios.

Los pesos **son coeficientes de puntuación**, no porcentajes de contribución efectiva al valor obtenido. La función describe el criterio que se intenta maximizar; **la implementación no resuelve exactamente este máximo**.

### 7.1 Procedimiento y restricciones

- **Separación mínima:** 250 m entre estaciones nuevas y respecto a estaciones existentes.
- **Conexión:** distancia euclidiana de como máximo 500 m a la red original o a otra estación nueva conectada.
- **Estrategia conectada:** cada estación elegida se integra geométricamente a la red ya existente, directa o indirectamente mediante otras nuevas.
- **Estrategia mixta:** además de extensiones, puede formar **núcleos independientes** conectados internamente, de al menos **cinco** estaciones nuevas; el mínimo se ha contrastado también con **siete y diez**.
- **Cobertura marginal:** después de incorporar cada estación o grupo, se actualizan las manzanas pendientes de cubrir.
- **Selección heurística:** se comparan extensiones individuales y, en la mixta, grupos de nuevas estaciones con un puntaje relativo por estación; el proceso es iterativo y **no garantiza un óptimo global**.

El centroide es una referencia geométrica. La conexión definida por 500 m en línea recta **no equivale a una conexión real sobre calles o ciclovías**.

## 8. Resultados y sensibilidad de la optimización

### 8.1 Escenario de referencia (`K = 10`, pesos 65/35)

| Indicador | Exclusivamente conectada (referencia) | Mixta (alternativa) |
|---|---:|---:|
| Población incremental | **94,496** | **157,606** |
| Movimientos diarios predichos, suma | **2,063.57** | **1,634.93** |
| Núcleos independientes | **0** | **2**, de cinco estaciones cada uno |
| Estaciones nuevas directamente a ≤ 500 m de la red original | **2** | **0** |

La cobertura geográfica estimada pasa de **12.77 % a 13.80 %** con la conectada. La alternativa mixta cubre **63,110 habitantes más** pero suma **428.64 movimientos diarios predichos menos**. Sus dos núcleos están separados de la red original; la distancia media a esta fue aproximadamente **0.86 km** en el primero y **1.69 km** en el segundo.

La conectada se adopta como **referencia metodológica** por su vínculo geométrico con la red original, no porque exista evidencia de superioridad operativa o predictiva. Los movimientos predichos **no son viajes netos adicionales**.

### 8.2 Sensibilidad a los pesos

Se evaluaron 21 combinaciones de coeficientes cobertura/actividad entre 100/0 y 0/100, con `K = 10`, para ambas estrategias. Algunos resultados ilustrativos:

| Pesos | Cobertura conectada | Movimientos conectada | Cobertura mixta | Movimientos mixta |
|---|---:|---:|---:|---:|
| 70/30 | 125,287 | 1,745.49 | 157,606 | 1,634.93 |
| 65/35 | 94,496 | 2,063.57 | 157,606 | 1,634.93 |
| 60/40 | 87,621 | 2,146.88 | 99,466 | 2,030.37 |
| 50/50 | 80,140 | 2,055.69 | 79,559 | 2,169.60 |

El **65/35 es un escenario de referencia**, no una preferencia universal ni una solución matemáticamente óptima. En la mixta, al cambiar a 60/40 la cobertura cae de 157,606 a 99,466 y el nivel de actividad predicha crece de 1,634.93 a 2,030.37. La diferencia de cobertura entre la mixta y la conectada pasa de 63,110 a 11,845 habitantes. **Parte del contraste entre estrategias depende de la ponderación y de los saltos de la heurística**.

### 8.3 Tamaño mínimo de los núcleos

Se contrastaron mínimos de **5, 7 y 10** estaciones por núcleo, en escenarios de pesos 100/0, 75/25 y 50/50. Por ejemplo, con 100/0, el tamaño 7 produjo **155,295** habitantes incrementales y el tamaño 10 produjo **157,597**. La falta de monotonía entre esas soluciones ilustra que **la heurística no garantiza encontrar el mejor portafolio factible**. La tabla completa se conserva en el análisis de optimización y en el apéndice del informe académico.

## 9. Supuestos y limitaciones

| Supuesto de trabajo | Límite o riesgo | Verificación futura |
|---|---|---|
| Relaciones aprendidas de estaciones existentes aplicables a ubicaciones nuevas | Sesgo de selección y extrapolación fuera de la red | Piloto o estaciones inauguradas en años posteriores |
| `(retiros + arribos) / 365` aproxima actividad diaria | Días no operativos y restricciones por bicicletas/anclajes | Días operativos y capacidad por estación |
| Un punto de manzana a 500 m está cubierto | Barreras físicas y rutas reales | Distancias de red peatonal; radios alternativos |
| Censo 2020 aproxima la distribución de población en 2025–2026 | Cambios demográficos desiguales | Datos actualizados y análisis de sensibilidad |
| Movimientos predichos de candidatas permanecen fijos | Sustitución de viajes y complementariedad entre estaciones | Seguimiento antes/después de expansiones |
| Un núcleo de cinco estaciones es una alternativa evaluable | No asegura infraestructura ni funcionamiento independiente | Evaluación de operación y redistribución de bicicletas |
| Conexión euclidiana ≤ 500 m representa conectividad | No considera continuidad de ciclovías o seguridad | Análisis sobre la red vial/ciclista real |

Además, no se incorporan restricciones presupuestales, permisos, capacidad de estación, disponibilidad física del sitio ni equidad socioeconómica como criterio explícito. El proyecto **prioriza ubicaciones para evaluación posterior**, no valida obras concretas.

## 10. Estado de implementación y trabajo pendiente

### Análisis implementados y documentados

- Integración de fuentes, EDA y métricas de cobertura.
- Entrenamiento y comparación de modelos, con validación cruzada espacial y evaluación de robustez.
- Generación de cuadrículas y predicción de actividad para candidatas.
- Heurística de escenarios conectados y mixtos; análisis de ponderaciones y tamaño de núcleos.
- Preparación de datos de entrada del tablero y contraste del motor con el notebook en escenarios analizados.

### Pendiente o no verificado como completo

1. **Comparaciones de referencia e incertidumbre:** portafolios aleatorios y otras bases; intervalo para la suma de actividades predichas y la diferencia entre estrategias.
2. **Presentación de resultados:** consolidación de mapas y figuras, además de revisión editorial de cifras y citas.
3. **Reproducción del repositorio:** instrucciones probadas en un entorno limpio, dependencias fijadas, acceso a datos/archivos procesados, empaquetado en Docker y tablero accesible en línea.
4. **Validación externa futura:** medición de actividad real de estaciones instaladas en zonas nuevas; la validación espacial sobre estaciones existentes no la sustituye.

## 11. Archivos y fuentes

Los notebooks principales del flujo son `EDA_v1`–`EDA_v6`, `Modelado_v1`, `Variables_v1_Candidatas` y `Optimizacion_v1`. El motor `motor_ecobici.py` se usa desde el notebook de optimización; dicho notebook exporta insumos hacia `../Data/Procesados/Tablero/`. **Esas rutas y su disponibilidad en el repositorio publicado deben comprobarse antes de afirmar que el proyecto se ejecuta desde cero**.

Fuentes principales:

- [ECOBICI — datos abiertos](https://ecobici.cdmx.gob.mx/datos-abiertos/)
- [INEGI — Censo de Población y Vivienda 2020](https://www.inegi.org.mx/programas/ccpv/2020/)
- [INEGI — DENUE](https://www.inegi.org.mx/app/mapa/denue/)
- [Datos Abiertos CDMX — Metro](https://datos.cdmx.gob.mx/dataset/lineas-y-estaciones-del-metro)
- [Datos Abiertos CDMX — Metrobús](https://datos.cdmx.gob.mx/dataset/geolocalizacion-metrobus)
- [Datos Abiertos CDMX — infraestructura ciclista](https://datos.cdmx.gob.mx/dataset/infraestructura-vial-ciclista)

---

*Esta documentación describe el método y los resultados disponibles al corte indicado. Las cifras son estimaciones sujetas a los supuestos y limitaciones expresados; no son predicciones verificadas de la operación de futuras estaciones.*
