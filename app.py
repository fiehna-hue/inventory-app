import os
import time
from contextlib import closing

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def run(sql, params=None, fetch=False):
    with closing(get_conn()) as conn:
        with conn, conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall() if fetch else None


def init_db():
    for _ in range(20):
        try:
            run(
                "CREATE TABLE IF NOT EXISTS items ("
                "id SERIAL PRIMARY KEY, "
                "name TEXT NOT NULL, "
                "quantity INT NOT NULL DEFAULT 0)"
            )
            return
        except psycopg2.OperationalError:
            time.sleep(1)
    raise RuntimeError("database not reachable")


init_db()


@app.get("/health")
def health():
    try:
        run("SELECT 1", fetch=True)
        return jsonify(status="ok")
    except Exception:
        return jsonify(status="db unreachable"), 503


@app.get("/items")
def list_items():
    rows = run("SELECT id, name, quantity FROM items ORDER BY id", fetch=True)
    return jsonify([{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows])


@app.post("/items")
def add_item():
    data = request.get_json(force=True)
    rows = run(
        "INSERT INTO items (name, quantity) VALUES (%s, %s) RETURNING id",
        (data["name"], data.get("quantity", 0)),
        fetch=True,
    )
    return jsonify(id=rows[0][0]), 201