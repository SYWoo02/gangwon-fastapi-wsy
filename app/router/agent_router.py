# app/router/agent_router.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any

from app.service.agent_service import AgentService
from app.deps import get_agent_service, get_vector_service

router = APIRouter(prefix="", tags=["agent"])


class KnowledgeRequest(BaseModel):
    office_name: str
    timezone: str
    country: str
    description: str


class QueryRequest(BaseModel):
    query: str

@router.post("/knowledge")
def add_knowledge(
    requests: list[KnowledgeRequest],
    agent_service: AgentService = Depends(get_agent_service),
):
    agent_service.add_knowledge_bulk(requests)
    return {
        "status": "success",
        "count": len(requests)
    }


# @router.post("/knowledge")
# def add_knowledge(requests: list[dict]):
#     return requests


@router.post("/query")
def query_agent(
    request: QueryRequest,
    agent_service: AgentService = Depends(get_agent_service),
):
    return agent_service.process_query(request.query)

@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Agent service is running"}


@router.get("/debug/vector")
def debug_vector():
    vs = get_vector_service()
    return {"status": "vector ok"}
