# postgreSQL.py
import os
import psycopg2
from psycopg2 import sql
from decimal import Decimal

# --- CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ---
HOST = os.getenv("DB_HOST", "localhost")
PORT = int(os.getenv("DB_PORT", 5432))
USER = os.getenv("DB_USER", "michel_user")
PASSWORD = os.getenv("DB_PASSWORD", "123456789")
DB_NAME = os.getenv("DB_NAME", "scraper_db")
TABLE_PRODUCTS = "products"
TABLE_TASKS = "tasks"

# --- CONEXIÓN ---
def conectar(db=DB_NAME):
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=db
    )

# --- CREAR BASE DE DATOS Y TABLAS ---
def create_database_if_not_exists():
    conn = psycopg2.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, dbname="postgres")
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (DB_NAME,))
    exists = cur.fetchone()
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"Base de datos '{DB_NAME}' creada.")
    else:
        print(f"Base de datos '{DB_NAME}' ya existe.")

    cur.close()
    conn.close()

def create_tables_if_not_exists():
    conn = conectar()
    cur = conn.cursor()

    # Tabla de productos
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_PRODUCTS} (
        id SERIAL PRIMARY KEY,
        job_id TEXT NOT NULL,
        name TEXT NOT NULL,
        price NUMERIC,
        description TEXT,
        image_url TEXT
    );
    """)

    # Tabla de tareas
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_TASKS} (
        job_id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        error_message TEXT
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Tablas '{TABLE_PRODUCTS}' y '{TABLE_TASKS}' listas.")

# --- PRODUCTOS ---
def insert_data_for_job(job_id, data):
    conn = conectar()
    cur = conn.cursor()

    # Borrar productos previos de este job_id para no duplicar
    cur.execute(f"DELETE FROM {TABLE_PRODUCTS} WHERE job_id=%s;", (job_id,))

    # Insertar nuevos productos
    for prod in data:
        price_val = prod["price"]
        if isinstance(price_val, str):
            # Convertir a Decimal si viene como string con "$"
            price_val = Decimal(price_val.replace("$", "").replace(",", ".")) if price_val else None
        cur.execute(
            f"INSERT INTO {TABLE_PRODUCTS} (job_id, name, price, description, image_url) VALUES (%s, %s, %s, %s, %s)",
            (job_id, prod["name"], price_val, prod["description"], prod.get("image_url", ""))
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Datos insertados correctamente para job_id '{job_id}'.")

def get_products_by_job(job_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"SELECT name, price, description, image_url FROM {TABLE_PRODUCTS} WHERE job_id=%s", (job_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"name": r[0], "price": r[1], "description": r[2], "image_url": r[3]} for r in rows]

# --- TAREAS ---
def create_task(job_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO {TABLE_TASKS} (job_id, status) VALUES (%s, %s) ON CONFLICT (job_id) DO NOTHING;",
        (job_id, "pending")
    )
    conn.commit()
    cur.close()
    conn.close()

def update_task_status(job_id, status, error_message=None):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"UPDATE {TABLE_TASKS} SET status=%s, error_message=%s WHERE job_id=%s", (status, error_message, job_id))
    conn.commit()
    cur.close()
    conn.close()

def get_task(job_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"SELECT status, error_message FROM {TABLE_TASKS} WHERE job_id=%s", (job_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        status, error_message = row
        return {"status": status, "error_message": error_message}
    return None
