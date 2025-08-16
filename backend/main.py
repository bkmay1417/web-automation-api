# main.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import asyncio
import uuid
from urllib.parse import urlparse
from decimal import Decimal

import postgreSQL
from scraper import scrape_products

PORT = 8000

class RequestHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # Convertir Decimal a float automáticamente
        def default_converter(o):
            if isinstance(o, Decimal):
                return float(o)
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

        # JSON con indentación para lectura más clara
        pretty_json = json.dumps(data, default=default_converter, indent=4)
        self.wfile.write(pretty_json.encode("utf-8"))

    def do_POST(self):
        if self.path == "/tasks":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
                task_id = data.get("task_id")
                lookup_key = data.get("lookup_key")
                if not task_id:
                    self._send_json({"error": "Debe ingresar un task_id, por ejemplo 'saucedemo'"}, 400)
                    return

                # Crear job_id único y registrar tarea
                job_id = str(uuid.uuid4())
                postgreSQL.create_task(job_id)

                # Ejecutar scraper bloqueante
                try:
                    _, products = asyncio.run(scrape_products(task_id=task_id, lookup_key=lookup_key))
                except Exception as e:
                    postgreSQL.update_task_status(job_id, "failed", str(e))
                    self._send_json({"job_id": job_id, "status": "failed", "error_message": str(e)}, 500)
                    return

                # Guardar productos en la DB
                postgreSQL.insert_data_for_job(job_id, products)
                postgreSQL.update_task_status(job_id, "completed")

                self._send_json({"job_id": job_id, "status": "completed"}, 202)

            except json.JSONDecodeError:
                self._send_json({"error": "JSON inválido"}, 400)

        else:
            self._send_json({"error": "Endpoint no encontrado"}, 404)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip("/").split("/")

        if len(path_parts) == 2 and path_parts[0] == "tasks":
            job_id = path_parts[1]
            task_info = postgreSQL.get_task(job_id)
            if not task_info:
                self._send_json({"error": f"No existe tarea con job_id {job_id}"}, 404)
                return

            status = task_info["status"]
            if status == "completed":
                products = postgreSQL.get_products_by_job(job_id)
                # Convertir Decimal a float antes de enviar JSON
                for p in products:
                    for k, v in p.items():
                        if isinstance(v, Decimal):
                            p[k] = float(v)
                # Respuesta con indentación para fácil lectura
                self._send_json({
                    "status": status,
                    "data": products
                })
            elif status == "failed":
                self._send_json({
                    "status": status,
                    "error_message": task_info.get("error_message", "Error desconocido")
                })
            else:
                self._send_json({"status": status})
        else:
            self._send_json({"error": "Endpoint no encontrado"}, 404)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), RequestHandler)
    print(f"Servidor escuchando en puerto {PORT}...")
    server.serve_forever()
