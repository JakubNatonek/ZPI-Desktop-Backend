from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.apis.api_login import router as login_router
#from app.database import Base, engine

# Create database tables
#Base.metadata.create_all(bind=engine)

app = FastAPI(title="ZPI Desktop Backend")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(login_router)



@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}
