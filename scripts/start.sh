#!/usr/bin/env bash
set -euo pipefail

pip install --no-cache-dir -r requirements.txt

python - <<'PY'
import os
import time
import pymysql

host = os.getenv("DB_HOST", "mysql")
port = int(os.getenv("DB_PORT", "3306"))
user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD", "")
database = os.getenv("DB_NAME", "sc-hangar-manager")

for i in range(60):
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=2,
            read_timeout=2,
            write_timeout=2,
            autocommit=True,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        print("MySQL is ready")
        break
    except Exception as err:
        print(f"Waiting for MySQL ({i + 1}/60): {err}")
        time.sleep(2)
else:
    raise SystemExit("MySQL is not available after timeout")
PY

alembic upgrade head

python - <<'PY'
from pathlib import Path
from sqlalchemy import create_engine, text
from app.config import Config

sql_path = Path("scripts/init.sql")
sql = sql_path.read_text(encoding="utf-8")

statements = [s.strip() for s in sql.split(";") if s.strip()]
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
with engine.begin() as conn:
    for statement in statements:
        conn.execute(text(statement))

print("Seed data applied")
PY

flask --app app.main run --host=0.0.0.0 --port=8000
