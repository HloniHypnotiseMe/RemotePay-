from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
from datetime import datetime

router = APIRouter()

# In-memory storage
assistants_db: Dict[str, dict] = {}

class AssistantConfig(BaseModel):
    name: str
    personality: str = "professional"
    greeting: Optional[str] = None
    business_type: Optional[str] = None

class AssistantResponse(BaseModel):
    id: str
    name: str
    personality: str
    greeting: str
    business_type: Optional[str]
    created_at: str

@router.post("/assistant/config", response_model=AssistantResponse)
async def configure_assistant(config: AssistantConfig):
    assistant_id = f"ast_{uuid.uuid4().hex[:8]}"
    assistants_db[assistant_id] = {
        "id": assistant_id,
        "name": config.name,
        "personality": config.personality,
        "greeting": config.greeting or f"Hi! I'm {config.name}, your Online Business Assistant! How can I help grow your business today?",
        "business_type": config.business_type,
        "created_at": datetime.now().isoformat()
    }
    return assistants_db[assistant_id]

@router.get("/assistant/{assistant_id}", response_model=AssistantResponse)
async def get_assistant(assistant_id: str):
    if assistant_id not in assistants_db:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return assistants_db[assistant_id]

@router.get("/assistant/{assistant_id}/greeting")
async def get_greeting(assistant_id: str):
    if assistant_id not in assistants_db:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return {"greeting": assistants_db[assistant_id]["greeting"]}
