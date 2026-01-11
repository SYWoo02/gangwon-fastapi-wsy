from fastapi import FastAPI, Request
from app.router.agent_router import router as agent_router

app = FastAPI(
    title="HW Day3",
    version="1.0.0",
)

app.include_router(agent_router)