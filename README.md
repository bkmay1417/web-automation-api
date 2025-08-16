
## Descripción General
Este proyecto es una **API REST** en Python que automatiza la extracción de datos de productos de sitios web utilizando **Playwright**.  
Los datos extraídos se normalizan y se almacenan en una base de datos **PostgreSQL**, y la API permite consultar el estado de las tareas y los resultados.

**Tecnologías utilizadas:**
- Python 3
- FastAPI
- Playwright
- PostgreSQL
- Docker / Docker Compose

---

## Endpoints de la API

### 1. POST /tasks
Inicia una nueva tarea de scraping.

**Request JSON:**
json
{
  "task_id": "nombre_del_sitio",
  "lookup_key": "opcional_busqueda"
}
json

Response:

{
  "job_id": "uuid_generado",
  "status": "accepted"
}


## 2. Endpoints de la API

### POST /tasks
Inicia una nueva tarea de scraping.

**Request JSON:**
json
{
  "task_id": "nombre_del_sitio",
  "lookup_key": "opcional_busqueda"
}
Response:

{
  "job_id": "uuid_generado",
  "status": "accepted"
}

GET /tasks/{job_id}

Consulta el estado de una tarea de scraping.

Response si la tarea está en progreso:

{
  "status": "in_progress"
}


Response si la tarea está completada:

{
  "status": "completed",
  "data": [
      {
      "name": "Nombre del producto",
      "price": "Precio",
      "description": "Descripción",
      "image_url": "URL_desde_el_backend"
    }
  ]
}


Response si la tarea falla:

{
  "status": "failed",
  "error_message": "Mensaje de error"
}

Configuración

Instalar Docker y Docker Compose.

Clonar el repositorio:

git clone https://github.com/tu_usuario/web-automation-backend.git
cd web-automation-backend


Crear archivo .env con la configuración de la base de datos:

POSTGRES_USER=usuario
POSTGRES_PASSWORD=contraseña
POSTGRES_DB=nombre_db

Cómo ejecutar

Levantar los servicios con Docker Compose:

docker-compose up --build


La API estará disponible en http://localhost:8000.

Sitios soportados

SauceDemo

Practice Software Testing

Notas

La extracción de datos incluye: nombre, precio, descripción e imagen del producto.

Las imágenes se almacenan localmente y se sirven desde el backend.

El proyecto cumple con los endpoints obligatorios (POST /tasks y GET /tasks/{job_id}) y los requerimientos mínimos del desafío.
