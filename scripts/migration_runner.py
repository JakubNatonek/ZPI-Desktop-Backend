import subprocess

def run_migrations():
    """Run Alembic migrations automatically at startup."""
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
    except Exception as e:
        print(f"Alembic migration failed: {e}")
