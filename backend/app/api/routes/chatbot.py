from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from app.models.audit import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: Optional[List[dict]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage
):
    """Send a message to the AI chatbot (public - no auth required)."""
    from app.services.chatbot_service import ChatbotService

    chatbot_service = ChatbotService()
    result = await chatbot_service.chat(
        message=message.message,
        conversation_id=message.conversation_id
    )

    return result


@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user)
):
    """Get user's conversation history."""
    # This would typically retrieve from database
    return []


@router.get("/faq")
async def get_faq():
    """Get frequently asked questions."""
    return [
        {
            "question": "Bagaimana saya boleh memohon bantuan zakat?",
            "answer": "Anda boleh memohon bantuan zakat dengan melengkapkan borang permohonan di pejabat Zakat atau secara online melalui sistem ini. Sila sediakan dokumen seperti IC, slip gaji, dan bil utiliti."
        },
        {
            "question": "Apakah syarat kelayakan menerima bantuan zakat?",
            "answer": "Syarat kelayakan termasuk: (1) Muslim, (2) Warganegara Malaysia atau bermastautin, (3) Pendapatan isi rumah di bawah paras garispanduan, (4) Mempunyai dokumen sokongan yang sah."
        },
        {
            "question": "Berapa lama masa pemprosesan permohonan?",
            "answer": "Masa pemprosesan biasanya mengambil masa 14-30 hari bekerja bergantung kepada kesempurnaan dokumen dan semakan diperlukan."
        },
        {
            "question": "Bagaimana saya boleh semak status permohonan?",
            "answer": "Anda boleh semak status permohonan dengan menggunakan nombor rujukan yang diberikan apabila menghantar permohonan. Sila hubungi pejabat Zakat atau gunakan sistem pertanyaan dalam talian."
        },
        {
            "question": "Apakah jenis bantuan yang disediakan?",
            "answer": "Sistem Zakat menyediakan pelbagai bantuan termasuk: bantuan bulanan untuk fakir dan miskin, bantuan pendidikan, bantuan perubatan, bantuan bencana, dan bantuan perniagaan untuk asnaf yang tertentu."
        }
    ]


@router.post("/feedback")
async def submit_feedback(
    conversation_id: str,
    rating: int,
    feedback: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Submit feedback for chatbot response."""
    # Save feedback to database
    return {"status": "success", "message": "Feedback received"}