from fastapi.params import Depends
from app.service.vector_service import VectorService
from app.service.embedding_service import EmbeddingService
from app.repository.vector_repo import ChromaDBRepository
from app.service.time_service import TimeService
from app.service.agent_service import AgentService

def get_vector_repository():
    return ChromaDBRepository()


def get_embedding_service():
    return EmbeddingService()


def get_vector_service():
    try:
        vector_repo = get_vector_repository()
        embedding_service = get_embedding_service()
        return VectorService(
            vector_repository=vector_repo,
            embedding_service=embedding_service,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise

# =========================
# Tool Service
# =========================

def get_time_service():
    return TimeService()

# =========================
# Agent Service
# =========================

def get_agent_service():
    try:
        vector_service = get_vector_service()
        time_service = get_time_service()

        return AgentService(
            vector_service=vector_service,
            time_service=time_service,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise