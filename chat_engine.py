from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from models import PrivacyVault, UserProfile

try:
    from groq import Groq

    _GROQ_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    _GROQ_AVAILABLE = False
    Groq = None

try:  # optional .env loading
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


class PayrollChatbot:
    SYSTEM_PROMPT = (
        "You are a helpful HR Assistant. Explain the payroll calculation to the user "
        "clearly. Be empathetic. Use the provided context."
    )

    def __init__(self) -> None:
        self._openai_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        self._model_name = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
        self._llm: Optional[Any] = None
        self._debug = os.getenv("CHATBOT_DEBUG", "").lower() in {"1", "true", "yes"}

    def _debug_log(self, message: str) -> None:
        if self._debug:
            print(f"[PayrollChatbot] {message}")

    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = dict(context)
        user_data = sanitized.get("user")
        if isinstance(user_data, UserProfile):
            sanitized["user"] = PrivacyVault.anonymize_user(user_data)
        elif isinstance(user_data, dict) and {"id", "name", "role", "hourly_rate"}.issubset(
            user_data.keys()
        ):
            user_profile = UserProfile(**user_data)
            sanitized["user"] = PrivacyVault.anonymize_user(user_profile)
        return sanitized

    def _build_llm_client(self) -> Optional[Any]:
        if not self._openai_key:
            self._debug_log("GROQ_API_KEY/OPENAI_API_KEY missing; using mock response.")
            return None
        if not _GROQ_AVAILABLE:
            self._debug_log("Groq SDK not installed; using mock response.")
            return None
        if self._llm is None:
            self._debug_log("Initializing Groq client.")
            self._llm = Groq(api_key=self._openai_key)
        return self._llm

    def _mock_response(self, query: str, context: Dict[str, Any]) -> str:
        normalized = query.lower()
        if "tax" in normalized:
            gross_pay = (
                context.get("payroll_record", {}).get("gross_pay")
                if isinstance(context.get("payroll_record"), dict)
                else None
            )
            if gross_pay is not None:
                return (
                    f"Your tax was calculated at 10% of your gross pay of ${gross_pay:.2f}."
                )
            return "Your tax was calculated at 10% of your gross pay."
        return (
            "I’m here to help explain your payroll details. Could you share which part "
            "you want clarified?"
        )

    def get_response(self, query: str, context: Dict[str, Any]) -> str:
        sanitized_context = self._sanitize_context(context)
        llm = self._build_llm_client()
        if llm:
            payload = json.dumps(sanitized_context, indent=2, default=str)
            self._debug_log(f"Calling Groq model '{self._model_name}'.")
            try:
                response = llm.chat.completions.create(
                    model=self._model_name,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"User question: {query}\n\nContext:\n{payload}",
                        },
                    ],
                )
                return response.choices[0].message.content
            except Exception as exc:  # pragma: no cover - runtime diagnostics
                self._debug_log(f"Groq request failed: {exc}")
        return self._mock_response(query, sanitized_context)
