import logging

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from config import FRONTEND_URL
from routers import chat, users, calendar, wellbeing, appointments, conversations

app = FastAPI(title="NeuroNav API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(users.router)
app.include_router(calendar.router)
app.include_router(wellbeing.router)
app.include_router(appointments.router)
app.include_router(conversations.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
