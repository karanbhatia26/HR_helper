# Payroll Models

This folder contains core data models and a small privacy utility for handling PII.

## What's inside
- `models.py`: Pydantic models for user profiles, timesheets, and payroll records, plus `PrivacyVault` helpers.
- `agent_logic.py`: `PayrollOrchestrator` workflow for ingestion, calculation, and audit logic.
- `chat_engine.py`: `PayrollChatbot` for answering payroll questions with anonymized context.

## Quick check
The following Python snippet validates the PII scrubber and anonymization output.

```python
from models import UserProfile, PrivacyVault

user = UserProfile(id="1", name="Jane Doe", role="Engineer", hourly_rate=50)
print(PrivacyVault.scrub_pii("Email jane@example.com"))
print(PrivacyVault.anonymize_user(user))

from agent_logic import PayrollOrchestrator

orchestrator = PayrollOrchestrator()
print(orchestrator.run_pipeline("Weekly report with overtime", user.hourly_rate))

from chat_engine import PayrollChatbot

chatbot = PayrollChatbot()
print(chatbot.get_response("Why is my tax higher?", result))
```

## Optional LLM setup
`PayrollChatbot` supports Groq via the official Groq Python SDK.

- `GROQ_API_KEY`: Required for Groq.
- `LLM_MODEL`: Model name (default: `openai/gpt-oss-120b`).

## Runner
Use `run_chatbot.py` for a quick end-to-end demo. It assembles a pipeline context and asks
the chatbot a sample payroll question.

If you want to configure Groq locally, copy `.env.example` to `.env` and fill in `GROQ_API_KEY`.
