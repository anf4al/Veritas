import pytest
from unittest.mock import patch, MagicMock
from backend.app.core.config import settings, validate_provider_keys
from backend.app.llm.groq_provider import GroqProvider, sanitize_error_message
from backend.app.llm.mock_provider import MockProvider
from backend.app.llm.factory import get_llm_provider

def test_groq_provider_configuration():
    """Requirement 9: Groq provider configured via environment without hardcoding or key leakage."""
    assert settings.GROQ_BASE_URL == "https://api.groq.com/openai/v1"
    assert settings.GROQ_MODEL != ""

    provider_info = validate_provider_keys()
    assert "GROQ_API_KEY" not in provider_info
    assert "provider" in provider_info

    # Key sanitization: verify keys are never leaked in error messages
    raw_error = "Error from Groq API with gsk_secret_1234567890abcdef on server"
    sanitized = sanitize_error_message(raw_error, "gsk_secret_1234567890abcdef")
    assert "gsk_secret_1234567890abcdef" not in sanitized
    assert "[REDACTED_API_KEY]" in sanitized

def test_groq_provider_initialization_error():
    """Missing key raises actionable error without creating invalid client."""
    provider = GroqProvider(api_key="")
    with pytest.raises(RuntimeError) as exc_info:
        provider._ensure_client()
    assert "Groq API key is missing" in str(exc_info.value)

def test_mock_provider_evidence_grounding_dynamic():
    """Requirement 10: Changing retrieved evidence dynamically changes MockProvider output
    without hardcoded question matching.
    """
    mock = MockProvider()

    # Case A: Context contains 20 days leave
    prompt_a = """<untrusted_enterprise_evidence>
[Evidence 1] Document: 'Annual Leave Policy' | Page: 2 | Section: 'Entitlement' | Version: '2.0' | Effective: '2026-01-01'
Content:
Full-time employees receive twenty (20) business days of paid annual leave each calendar year.
</untrusted_enterprise_evidence>

User Question: How many leave days do I get?

Provide answer with citations."""

    ans_a = mock._generate_grounded_response(prompt_a)
    assert "twenty (20) business days" in ans_a
    assert "[Doc: Annual Leave Policy" in ans_a
    assert "p.2" in ans_a

    # Case B: Context changed to 25 days leave and different document
    prompt_b = """<untrusted_enterprise_evidence>
[Evidence 1] Document: 'Executive Compensation Charter' | Page: 5 | Section: 'Vacation' | Version: '4.0' | Effective: '2026-06-01'
Content:
Executive tier employees receive twenty-five (25) vacation days annually.
</untrusted_enterprise_evidence>

User Question: How many leave days do I get?

Provide answer with citations."""

    ans_b = mock._generate_grounded_response(prompt_b)
    # Output must reflect the changed evidence
    assert "twenty-five (25) vacation days" in ans_b
    assert "[Doc: Executive Compensation Charter" in ans_b
    assert "p.5" in ans_b
    assert "twenty (20) business days" not in ans_b

def test_mock_provider_empty_evidence():
    """Empty evidence returns honest insufficiency message."""
    mock = MockProvider()
    ans = mock._generate_grounded_response("User Question: What is our space travel policy?")
    assert "insufficient evidence" in ans.lower()

