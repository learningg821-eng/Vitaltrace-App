from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

import models
import auth.models
from database import engine
from auth.router import router as auth_router
from routers import staff, roles, permissions, alerts,notifications,patients,vitals,dashboard,ledger,chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    auth.models.Base.metadata.create_all(bind=engine)

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connected successfully")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(staff.router)
app.include_router(roles.router)
app.include_router(permissions.router)
app.include_router(alerts.router)
app.include_router(notifications.router)
app.include_router(patients.router)
app.include_router(vitals.router)
app.include_router(dashboard.router)
app.include_router(ledger.router)
app.include_router(chat.router)