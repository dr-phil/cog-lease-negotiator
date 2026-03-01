"""
FastAPI application entrypoint for TowerLease Intelligence.

This serves as the backend for the Angular frontend (coming in Q2).
CORS is configured for localhost:4200 (Angular dev server).

To run:
    uvicorn towerlease.server.main:app --reload --port 8000
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from towerlease.server.routes import towers, negotiate, followup

app = FastAPI(
    title="TowerLease Intelligence",
    description="Internal AT&T tool for cell tower lease renegotiation preparation",
    version="1.2.0",  # bumped from 1.1.0 after adding follow-up Q&A
)

# CORS for Angular frontend dev server
# TODO: add production frontend URL when we deploy to staging -- JIRA-2245
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(towers.router)
app.include_router(negotiate.router)
app.include_router(followup.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "towerlease-intelligence"}
