import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = int(os.environ.get("DB_PORT"))
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


@app.route("/")
def index():
    return "Entry point is working. Try /items"


@app.route("/items")
def get_items():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    items = [{"id": r[0], "name": r[1]} for r in rows]
    return jsonify(items)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
