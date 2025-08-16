
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
