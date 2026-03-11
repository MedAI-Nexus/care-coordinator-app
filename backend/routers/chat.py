from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import logging
import traceback

from database import get_db
from schemas import ChatRequest
from agent.orchestrator import run_agent

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Handle a chat message. Returns SSE stream."""

    async def event_stream():
        try:
            async for chunk in run_agent(db, request.user_id, request.message):
                yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            logger.error(f"Chat error: {e}\n{traceback.format_exc()}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
