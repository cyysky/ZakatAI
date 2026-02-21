"""
Chatbot Service - RAG-based AI assistant
"""
from typing import Dict, Any, Optional, List
import uuid
from app.services.llm_service import LLMService, ZAKAT_CHATBOT_SYSTEM
from app.services.vector_store import VectorStoreService


class ChatbotService:
    """Service for the AI Smart Assistant (Chatbot)."""

    def __init__(self):
        self.llm_service = LLMService()
        self.vector_store = VectorStoreService()
        self.conversations = {}  # In-memory conversation storage

    async def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return a response.
        Uses RAG (Retrieval Augmented Generation) for better answers.
        """
        # Create new conversation if needed
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            self.conversations[conversation_id] = [
                {"role": "system", "content": ZAKAT_CHATBOT_SYSTEM}
            ]

        # Get conversation history
        conversation = self.conversations.get(conversation_id, [])
        if not conversation or conversation[0]["role"] != "system":
            conversation.insert(0, {"role": "system", "content": ZAKAT_CHATBOT_SYSTEM})
            self.conversations[conversation_id] = conversation

        # Retrieve relevant context from knowledge base
        context_docs = await self.vector_store.similarity_search(message, n_results=3)

        # Build context from retrieved documents
        context = self._build_context(context_docs)

        # Create enhanced prompt with context
        enhanced_prompt = self._create_prompt(message, context)

        # Get response from LLM
        response = await self.llm_service.generate(
            prompt=enhanced_prompt,
            system_prompt=ZAKAT_CHATBOT_SYSTEM,
            temperature=0.7,
            max_tokens=500
        )

        # Add user message and response to conversation history
        conversation.append({"role": "user", "content": message})

        if response.get("success"):
            response_text = response.get("response", "")

            # Check if response is mostly thinking - if so, use fallback
            thinking_markers = ["**Analyze", "**Determine", "**Drafting", "**Refining", "**Finaliz"]
            marker_count = sum(1 for m in thinking_markers if m in response_text)

            if marker_count >= 2 or len(response_text) > 1000:
                # Too much thinking - use fallback
                response_text = self._get_fallback_response(message)
            else:
                # Clean up any remaining thinking
                response_text = self._clean_thinking(response_text)

            conversation.append({"role": "assistant", "content": response_text})
        else:
            # Fallback to template response if LLM fails
            response_text = self._get_fallback_response(message)
            conversation.append({"role": "assistant", "content": response_text})

        self.conversations[conversation_id] = conversation

        return {
            "response": response_text,
            "conversation_id": conversation_id,
            "sources": self._format_sources(context_docs)
        }

    def _build_context(self, docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        if not docs:
            return ""

        context = "Maklumat yang mungkin berguna:\n\n"
        for i, doc in enumerate(docs, 1):
            context += f"{i}. {doc.get('text', '')}\n\n"

        return context

    def _create_prompt(self, message: str, context: str) -> str:
        """Create enhanced prompt with context."""
        if context:
            return f"""Berdasarkan konteks berikut, sila jawab soalan pengguna dengan tepat dan dalam Bahasa Melayu:

Konteks:
{context}

Soalan pengguna: {message}

Jawapan:"""

        return f"""Sila jawab soalan berikut dalam Bahasa Melayu dengan tepat dan helpful:

Soalan: {message}

Jawapan:"""

    def _format_sources(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for display."""
        sources = []
        for doc in docs:
            sources.append({
                "text": doc.get("text", "")[:100] + "...",
                "topic": doc.get("metadata", {}).get("topic", "unknown")
            })
        return sources

    def _get_fallback_response(self, message: str) -> str:
        """Get fallback response when LLM is not available."""
        message_lower = message.lower()

        # Simple keyword-based responses
        if "permohonan" in message_lower or "memohon" in message_lower or "apply" in message_lower:
            return ("Untuk memohon bantuan Zakat, anda boleh melengkapkan borang permohonan di "
                    "pejabat Zakat atau secara online. Sila sediakan dokumen seperti IC, slip gaji, "
                    "dan bil utiliti. Untuk maklumat lanjut, sila hubungi pejabat Zakat.")

        elif "kelayakan" in message_lower or "syarat" in message_lower:
            return ("Syarat kelayakan menerima Zakat adalah: (1) Muslim, (2) Warganegara Malaysia "
                    "atau bermastautin, (3) Pendapatan di bawah RM1169 sebulan untuk fakir, "
                    "(4) Mempunyai dokumen sokongan yang sah.")

        elif "status" in message_lower or "semak" in message_lower:
            return ("Untuk semak status permohonan, gunakan nombor rujukan yang diberikan. "
                    "Anda juga boleh hubungi pejabat Zakat untuk pertanyaan.")

        elif "bantuan" in message_lower or "jenis" in message_lower:
            return ("Sistem Zakat menyediakan: bantuan bulanan (RM100-RM500), bantuan pendidikan, "
                    "bantuan perubatan, bantuan bencana, dan bantuan perniagaan.")

        elif "alamat" in message_lower or "location" in message_lower:
            return ("Pejabat Zakat terletak di lokasi berdekatan dengan anda. "
                    "Anda juga boleh layari sistem untuk maklumat lanjut.")

        elif "hubungi" in message_lower or "contact" in message_lower:
            return ("Anda boleh hubungi pejabat Zakat terdekat atau "
                    "emel ke sistem untuk pertanyaan.")

        else:
            return ("Terima kasih atas pertanyaan anda. Untuk maklumat lanjut tentang "
                    "bantuan Zakat, sila hubungi pejabat Zakat atau "
                    "layari sistem dalam talian.")

    def _clean_thinking(self, text: str) -> str:
        """Remove thinking process from model output."""
        if not text:
            return text

        # Try to find "Main Answer:" or similar sections
        import re

        # Look for main answer sections
        main_answer_match = re.search(
            r'\*Main Answer:\*(.+?)(?:\d+\.\s+\*\*|$)',
            text,
            re.DOTALL
        )
        if main_answer_match:
            return main_answer_match.group(1).strip()

        # Look for "Final" sections
        final_match = re.search(
            r'(?:5\.\s+\*\*Finalizing|\*\*Final).*?:\s*(.+?)(?:\d+\.\s+|$)',
            text,
            re.DOTALL
        )
        if final_match:
            return final_match.group(1).strip()

        # Try to find content after numbered thinking points
        # Pattern: numbers like "4. ", "5. " followed by actual content
        lines = text.split('\n')
        response_lines = []
        capture = False

        for line in lines:
            # Skip lines that look like thinking steps
            if re.match(r'^\d+\.\s+\*\*', line):
                capture = True
                continue
            if capture and line.strip():
                # Stop if we hit another thinking marker
                if re.match(r'^\d+\.\s+\*\*', line):
                    break
                response_lines.append(line)

        if response_lines:
            cleaned = '\n'.join(response_lines).strip()
            if len(cleaned) > 20:
                return cleaned

        # Last resort: remove thinking pattern entirely
        cleaned = re.sub(
            r'^\d+\.\s+\*\*[^*]+\*\*:.+?(?=\d+\.\s+\*\*|$)',
            '',
            text,
            flags=re.DOTALL
        ).strip()

        # If still too long or has markers, use fallback
        if len(cleaned) > 500 or '**' in cleaned[:200]:
            return self._get_fallback_response(text[:50])

        return cleaned if cleaned else text

    async def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation history."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False

    async def get_conversation_history(
        self,
        conversation_id: str
    ) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversations.get(conversation_id, [])