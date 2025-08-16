# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir playwright psycopg2-binary
RUN playwright install

# Exponer puerto del backend
EXPOSE 8000

# Comando para arrancar la API
CMD ["python", "main.py"]
