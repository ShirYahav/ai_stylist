from fastapi import APIRouter, Body
from src.logic.chat.llama_chat import ChatSession

router = APIRouter()

sessions = {}  

@router.post("/chat")
def chat_with_model(user_id: str = Body(...), message: str = Body(...)):
    if user_id not in sessions:
        sessions[user_id] = ChatSession(user_id)
    session = sessions[user_id]
    reply = session.ask(message)
    return {"response": reply}