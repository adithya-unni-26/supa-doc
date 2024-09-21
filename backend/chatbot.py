from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from database import supabase
from auth import get_current_user
from document_processing import process_and_store_document

router = APIRouter()

class ChatbotCreate(BaseModel):
    name: str
    document_urls: List[str]

class ChatbotUpdate(BaseModel):
    name: Optional[str] = None
    document_urls: Optional[List[str]] = None

class Chatbot(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    created_at: str
    updated_at: str

@router.post("/chatbots", response_model=Chatbot)
async def create_chatbot(chatbot: ChatbotCreate, user_id: str = Depends(get_current_user)):
    # Insert chatbot into database
    result = supabase.table("chatbots").insert({"name": chatbot.name, "user_id": user_id}).execute()
    chatbot_id = result.data[0]["id"]
    
    # Insert associated documents and process them
    for url in chatbot.document_urls:
        document_result = supabase.table("documents").insert({"chatbot_id": chatbot_id, "url": url}).execute()
        document_id = document_result.data[0]["id"]
        process_and_store_document(url, document_id)
    
    return Chatbot(**result.data[0])

@router.get("/chatbots/{chatbot_id}", response_model=Chatbot)
async def get_chatbot(chatbot_id: UUID, user_id: str = Depends(get_current_user)):
    result = supabase.table("chatbots").select("*").eq("id", str(chatbot_id)).eq("user_id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return Chatbot(**result.data[0])

@router.put("/chatbots/{chatbot_id}", response_model=Chatbot)
async def update_chatbot(chatbot_id: UUID, chatbot: ChatbotUpdate, user_id: str = Depends(get_current_user)):
    update_data = chatbot.dict(exclude_unset=True)
    result = supabase.table("chatbots").update(update_data).eq("id", str(chatbot_id)).eq("user_id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    if chatbot.document_urls:
        # Delete existing documents
        supabase.table("documents").delete().eq("chatbot_id", str(chatbot_id)).execute()
        # Insert new documents
        for url in chatbot.document_urls:
            document_result = supabase.table("documents").insert({"chatbot_id": str(chatbot_id), "url": url}).execute()
            document_id = document_result.data[0]["id"]
            process_and_store_document(url, document_id)
    
    return Chatbot(**result.data[0])

@router.delete("/chatbots/{chatbot_id}", status_code=204)
async def delete_chatbot(chatbot_id: UUID, user_id: str = Depends(get_current_user)):
    result = supabase.table("chatbots").delete().eq("id", str(chatbot_id)).eq("user_id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Chatbot not found")