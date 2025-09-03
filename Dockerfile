# Dockerfile para Astro CLI
FROM quay.io/astronomer/astro-runtime:9.2.0

# Instalar dependencias del sistema
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

USER astro

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY airflow_utils /usr/local/airflow/airflow_utils
