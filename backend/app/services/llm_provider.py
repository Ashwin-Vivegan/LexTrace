import logging
import httpx
from abc import ABC, abstractmethod
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """
    Abstract Base Class for LLM Answer Generation Providers.
    """
    @abstractmethod
    def generate_answer(self, prompt: str, system_prompt: str) -> str:
        """
        Generates an evidence-grounded text completion based on prompt and system_prompt.
        """
        pass

class GroqLLMProvider(LLMProvider):
    """
    Groq LLM Provider using OpenAI-compatible Chat Completions API via HTTP.
    """
    GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, timeout: float = 30.0):
        import os
        self.api_key = api_key if api_key is not None else (settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY", ""))
        self.model = model if model is not None else (settings.GROQ_MODEL or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
        self.timeout = timeout

    def generate_answer(self, prompt: str, system_prompt: str) -> str:
        if not self.api_key or not self.api_key.strip():
            logger.error("Groq API key is missing or empty. Please set GROQ_API_KEY in backend/.env file.")
            raise ValueError("Groq API key missing. Please configure GROQ_API_KEY in your backend/.env file.")

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 1024
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.GROQ_ENDPOINT, headers=headers, json=payload)
                
                if response.status_code != 200:
                    logger.error(f"Groq API returned HTTP status {response.status_code}: {response.text}")
                    raise RuntimeError(f"Groq API error (HTTP {response.status_code}).")

                data = response.json()
                choices = data.get("choices", [])
                if not choices or "message" not in choices[0] or "content" not in choices[0]["message"]:
                    logger.error("Malformed response from Groq API.")
                    raise RuntimeError("Malformed response structure received from Groq API.")

                answer = choices[0]["message"]["content"].strip()
                return answer

        except httpx.TimeoutException:
            logger.error("Groq API request timed out.")
            raise RuntimeError("Groq API request timed out.")
        except httpx.RequestError as req_err:
            logger.error(f"Network error connecting to Groq API: {req_err}")
            raise RuntimeError("Network error connecting to Groq API.")
        except Exception as e:
            if not isinstance(e, (ValueError, RuntimeError)):
                logger.error(f"Unexpected error in Groq LLM generation: {e}")
                raise RuntimeError(f"LLM generation failed: {str(e)}")
            raise e
