from fastapi import FastAPI

app = FastAPI(title="ZPI Desktop Backend")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}
