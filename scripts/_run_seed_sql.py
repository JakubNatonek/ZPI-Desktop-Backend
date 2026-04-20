from pathlib import Path
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env')

sql_path = Path('scripts/seed_grades_panel_test.sql')
if not sql_path.exists():
    raise SystemExit(f'SQL file not found: {sql_path}')

sql_text = sql_path.read_text(encoding='utf-8')

host = os.getenv('POSTGRES_HOST', 'localhost')
user = os.getenv('POSTGRES_USER', 'postgres')
password = os.getenv('POSTGRES_PASSWORD', 'postgres')
database = os.getenv('POSTGRES_DB', 'zpi_db')

ports = []
for value in [os.getenv('POSTGRES_PORT', '5432'), '5433', '5432']:
    try:
        port = int(value)
    except Exception:
        continue
    if port not in ports:
        ports.append(port)

conn = None
last_error = None
for port in ports:
    try:
        print(f'Trying DB connection: {host}:{port}/{database} as {user}')
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=database,
        )
        print(f'Connected on port {port}')
        break
    except Exception as exc:
        last_error = exc
        print(f'Connection failed on port {port}: {exc}')

if conn is None:
    raise SystemExit(f'Cannot connect to database. Last error: {last_error}')

try:
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql_text)
            cur.execute("""
                SELECT login
                FROM users
                WHERE login IN ('student.oceny.test', 'wykladowca.oceny.test', 'admin.oceny.test')
                ORDER BY login
            """)
            logins = [row[0] for row in cur.fetchall()]
            print('Seed completed. Test users in DB: ' + ', '.join(logins))
finally:
    conn.close()
