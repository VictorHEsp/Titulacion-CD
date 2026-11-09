# Expansión de ECOBICI en la CDMX: predicción de actividad y optimización espacial

**Proyecto de titulación — Licenciatura en Ciencia de Datos, ITAM**  
**Autor:** Victor H. Esparza Díaz

## Objetivo

Identificar **cuadrículas de 250 × 250 m** en las que conviene instalar **K nuevas estaciones ECOBICI** en la Ciudad de México, equilibrando la **actividad diaria potencial predicha** y la **cobertura poblacional incremental**, sujeta a condiciones de separación y conectividad. El tablero interactivo permite explorar las recomendaciones; **no constituye el objetivo de investigación** ni sustituye una evaluación de factibilidad en campo.

## Metodología y resultados

Se analizan viajes de octubre de 2024 a septiembre de 2026, características urbanas y datos geográficos. Se comparan modelos predictivos mediante **GroupKFold espacial** (5 particiones, 28 bloques) utilizando información de 670 estaciones. Después, una heurística multicriterio selecciona entre **12,954 cuadrículas candidatas** para un número K de estaciones y ponderaciones definidas por el usuario.

En el escenario de referencia (**K = 10; 65 % cobertura y 35 % actividad**):

| Métrica | Solo conectada | Mixta |
|---|---:|---:|
| Habitantes cubiertos adicionalmente | 94,496 | 157,606 |
| Movimientos diarios estimados | 2,063.57 | 1,634.93 |
| Núcleos independientes | 0 | 2 |

El **Random Forest** obtuvo MAE espacial de **56.67 movimientos diarios por estación**, frente a **70.69** del modelo base que predice la mediana. La estrategia mixta ofrece mayor cobertura en este escenario, pero requiere evaluar la viabilidad de núcleos separados de la red actual.

## Reproducir los resultados (Docker)

**Requisitos:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) y Docker Compose. Desde la raíz del repositorio:

```bash
docker compose run --build --rm quick
```

Este comando vuelve a calcular los MAE por partición espacial, compara las estrategias de expansión y **verifica automáticamente los diez identificadores seleccionados y las cifras de referencia**. Guarda las tablas y figuras en `outputs/quick/`. Para incluir las tres búsquedas anidadas adicionales de hiperparámetros:

```bash
docker compose run --build --rm quick make quick-all
```

La prueba rápida se verificó en Python 3.13 tanto en el entorno local como en Docker. Se observó una pequeña diferencia en el MAE de XGBoost entre macOS y Docker (**58.78** frente a **59.01**); las cifras centrales de Random Forest y ambos escenarios coincidieron.

## Abrir el tablero

```bash
docker compose up --build dashboard
```

Abrir **http://localhost:8501**. El tablero permite elegir K, alcaldía, ponderaciones y estrategia de conectividad, visualizar las recomendaciones y exportarlas a CSV. Para detenerlo, usar `Ctrl + C`.

## Estructura del repositorio

- `Notebooks/`: nueve notebooks numerados de preparación, modelado y optimización.
- `src/motor_ecobici.py`: lógica de selección espacial reutilizable.
- `dashboard_ecobici.py`: aplicación Streamlit.
- `scripts/quick.py`: evaluación y pruebas automáticas de reproducción.
- `data/processed/`: tablas y archivos geográficos intermedios; `tablero/` contiene seis insumos de la aplicación.
- `data/raw/README.md`: inventario de fuentes originales y rutas de descarga.
- `metodologia.md`: desarrollo metodológico y limitaciones.

## Alcance de la reproducción y limitaciones

La ejecución `quick` **comienza con datos intermedios versionados**: reevalúa los modelos sobre las 670 estaciones y vuelve a optimizar los escenarios a partir de las predicciones y matrices ya calculadas. **No descarga los 24 CSV originales ni reconstruye desde cero las 12,954 predicciones de candidatas**; para ese flujo completo se incluyen los notebooks y el inventario de fuentes.

Los movimientos estimados no equivalen necesariamente a viajes nuevos netos. La extrapolación a zonas sin estaciones existentes presenta incertidumbre; la conectividad utiliza una aproximación geométrica y no incorpora por completo costos, permisos, seguridad ni condiciones físicas del sitio. Las ubicaciones son **recomendaciones de planeación**, no puntos definitivos de instalación.
