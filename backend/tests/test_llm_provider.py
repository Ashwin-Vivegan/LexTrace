import pytest
from unittest.mock import MagicMock, patch
import httpx
from app.services.llm_provider import GroqLLMProvider

def test_groq_provider_missing_key():
    provider = GroqLLMProvider(api_key="")
    with pytest.raises(ValueError, match="Groq API key missing"):
        provider.generate_answer(prompt="test", system_prompt="system")

@patch("httpx.Client.post")
def test_groq_provider_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "The agreement allows termination with 30 days notice."
                }
            }
        ]
    }
    mock_post.return_value = mock_response

    provider = GroqLLMProvider(api_key="gsk_mock_test_key")
    answer = provider.generate_answer(prompt="What are the termination rules?", system_prompt="You are a legal assistant.")
    assert "termination with 30 days notice" in answer

@patch("httpx.Client.post")
def test_groq_provider_timeout(mock_post):
    mock_post.side_effect = httpx.TimeoutException("Timeout")
    provider = GroqLLMProvider(api_key="gsk_mock_key")
    with pytest.raises(RuntimeError, match="timed out"):
        provider.generate_answer(prompt="test", system_prompt="system")

@patch("httpx.Client.post")
def test_groq_provider_http_error(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_post.return_value = mock_response

    provider = GroqLLMProvider(api_key="gsk_mock_key")
    with pytest.raises(RuntimeError, match="HTTP 401"):
        provider.generate_answer(prompt="test", system_prompt="system")
