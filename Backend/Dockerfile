FROM python:3.12-slim

WORKDIR /app

# Instala dependencias del sistema mínimas para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El código fuente se monta como volumen en desarrollo;
# en producción se copiaría aquí con: COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
