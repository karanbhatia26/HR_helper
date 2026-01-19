from agent_logic import PayrollOrchestrator
from models import UserProfile, PrivacyVault

user = UserProfile(id="1", name="Jane Doe", role="Engineer", hourly_rate=50)
print(PrivacyVault.scrub_pii("Email jane@example.com"))
print(PrivacyVault.anonymize_user(user))

orchestrator = PayrollOrchestrator()
result = orchestrator.run_pipeline("Weekly report with overtime", user.hourly_rate)
print(result)