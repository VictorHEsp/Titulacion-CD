# Reproduce el entorno de ejecución del proyecto (Python 3.13).
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

# libgomp1 es utilizado por librerías numéricas como XGBoost.
RUN apt-get update \
    && apt-get install -y --no-install-recommends make libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copiamos solamente los archivos necesarios para reproducir 'quick' y abrir el tablero.
COPY Makefile ./
COPY dashboard_ecobici.py ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY data/processed/datos_modelo_ECOBICI.csv ./data/processed/datos_modelo_ECOBICI.csv
COPY data/processed/tablero/ ./data/processed/tablero/

EXPOSE 8501
CMD ["make", "quick"]
