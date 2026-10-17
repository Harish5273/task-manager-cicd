import os
import psycopg
from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates") if os.path.basename(os.path.dirname(__file__)) == "backend" else os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=TEMPLATE_DIR)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/taskdb"
)


def get_connection():
    return psycopg.connect(DATABASE_URL)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS tasks "
                "(id SERIAL PRIMARY KEY, title TEXT NOT NULL)"
            )
            cur.execute("SELECT id, title FROM tasks ORDER BY id")
            tasks = [
                {"id": row[0], "title": row[1]}
                for row in cur.fetchall()
            ]

    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS tasks "
                "(id SERIAL PRIMARY KEY, title TEXT NOT NULL)"
            )
            cur.execute(
                "INSERT INTO tasks (title) VALUES (%s) RETURNING id",
                (title,)
            )
            task_id = cur.fetchone()[0]

    return jsonify({"id": task_id, "title": title}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
