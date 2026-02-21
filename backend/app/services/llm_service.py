"""
LLM Service - Local AI API integration (replaces Ollama)
"""
import httpx
from typing import Optional, Dict, Any, List
from app.core.config import settings


class LLMService:
    """Service for interacting with local AI API."""

    def __init__(self):
        self.base_url = settings.AI_API_URL
        self.api_key = settings.AI_API_KEY
        self.model = settings.LLM_MODEL

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """Generate text using the local AI API."""

        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    message = result.get("choices", [{}])[0].get("message", {})
                    # Handle models that return content in reasoning_content
                    content = message.get("content") or message.get("reasoning_content") or ""
                    return {
                        "success": True,
                        "response": content,
                        "done": True
                    }
                else:
                    return {
                        "success": False,
                        "error": f"AI API error: {response.status_code} - {response.text}"
                    }

        except httpx.ConnectError:
            return {
                "success": False,
                "error": "Cannot connect to AI API. Please check the server."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Chat with the AI using message history."""

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self._get_headers(),
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    message = result.get("choices", [{}])[0].get("message", {})
                    # Handle models that return content in reasoning_content
                    content = message.get("content") or message.get("reasoning_content") or ""
                    return {
                        "success": True,
                        "response": content,
                        "done": True
                    }
                else:
                    return {
                        "success": False,
                        "error": f"AI API error: {response.status_code}"
                    }

        except httpx.ConnectError:
            return {
                "success": False,
                "error": "Cannot connect to AI API. Please check the server."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings using the embedding model."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/embeddings",
                    headers=self._get_headers(),
                    json={
                        "model": settings.EMBEDDING_MODEL,
                        "input": text
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("data", [{}])[0].get("embedding", [])
                else:
                    print(f"Embedding error: {response.status_code} - {response.text}")
                    return []

        except Exception as e:
            print(f"Embedding generation error: {e}")
            return []

    async def is_available(self) -> bool:
        """Check if the AI API is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/v1/models",
                    headers=self._get_headers()
                )
                return response.status_code == 200
        except:
            return False

    async def list_models(self) -> List[str]:
        """List available models."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/v1/models",
                    headers=self._get_headers()
                )
                if response.status_code == 200:
                    data = response.json()
                    return [model["id"] for model in data.get("data", [])]
                return []
        except:
            return []


# Default system prompt for the chatbot
ZAKAT_CHATBOT_SYSTEM = """Anda adalah Smart Assistant untuk sistem pengurusan Zakat.
Tugas anda adalah untuk membantu pengguna dengan pertanyaan mengenai:
- Permohonan bantuan Zakat
- Status permohonan
- Syarat kelayakan
- Jenis-jenis bantuan yang disediakan

Sentiasa bersopan, helpful, dan berikan maklumat yang tepat.
Jika anda tidak pasti sesuatu jawapan, nasihatkan pengguna untuk hubungi pejabat berkaitan secara terus.

Jawapan anda perlu dalam Bahasa Melayu (selain untuk nama atau istilah teknikal).
"""