import subprocess


def run_migrations() -> None:
    """Run Alembic migrations automatically at startup."""
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
    except Exception as exc:
        print(f"Alembic migration failed: {exc}")
