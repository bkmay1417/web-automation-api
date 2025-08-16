# main.py
from http.server import BaseHTTPRequestHandler, HTTPServer
from scraper import scrape_products  # tu scraper ya implementado
import postgreSQL
import json
import asyncio
import uuid
from urllib.parse import urlparse, parse_qs

# Token secreto que tu cliente debe usar
SECRET_TOKEN = "MI_TOKEN_SECRETO"

class SimpleHandler(BaseHTTPRequestHandler):

    def _check_token(self):
        """Verifica si el request tiene el token correcto en query string"""
        query = urlparse(self.path).query
        params = parse_qs(query)
        token = params.get("token", [None])[0]
        return token == SECRET_TOKEN

    def do_GET(self):
        if not self._check_token():
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized: token missing or incorrect"}).encode("utf-8"))
            return

        if self.path.startswith("/scrape"):
            try:
                job_id = str(uuid.uuid4())
                postgreSQL.create_task(job_id)
                products = asyncio.run(scrape_products())
                postgreSQL.insert_data_for_job(job_id, products)
                postgreSQL.update_task_status(job_id, "completed")

                response = {
                    "job_id": job_id,
                    "products_count": len(products)
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif self.path.startswith("/tasks"):
            query = urlparse(self.path).query
            params = parse_qs(query)
            job_id = params.get("job_id", [None])[0]

            if not job_id:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "job_id is required"}).encode("utf-8"))
                return

            task = postgreSQL.get_task(job_id)
            if not task:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "task not found"}).encode("utf-8"))
                return

            if task["status"] == "completed":
                data = postgreSQL.get_products_by_job(job_id)
                response = {"status": "completed", "data": data}
            elif task["status"] == "failed":
                response = {"status": "failed", "error": task.get("error_message")}
            else:
                response = {"status": task["status"], "data": []}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), SimpleHandler)
    print("Servidor escuchando en puerto 8000...")
    server.serve_forever()
