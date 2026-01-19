from __future__ import annotations

from agent_logic import PayrollOrchestrator
from chat_engine import PayrollChatbot
from models import UserProfile


def main() -> None:
    user = UserProfile(id="1", name="Jane Doe", role="Engineer", hourly_rate=50.0)
    orchestrator = PayrollOrchestrator()
    result = orchestrator.run_pipeline("Weekly report with overtime", user.hourly_rate)
    result["user"] = user

    chatbot = PayrollChatbot()
    response = chatbot.get_response("Why is my tax higher?", result)
    print(response)


if __name__ == "__main__":
    main()
