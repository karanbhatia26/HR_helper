from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from models import PayrollRecord, PrivacyVault, Timesheet


class PayrollOrchestrator:
    def __init__(self) -> None:
        self._last_hours_claimed: float | None = None

    def extract_data(self, file_content: str) -> Timesheet:
        normalized = file_content.lower()
        hours = 50.0 if "overtime" in normalized else 40.0
        scrubbed_content = PrivacyVault.scrub_pii(file_content)
        return Timesheet(
            id=str(uuid4()),
            user_id="unknown",
            raw_text=scrubbed_content,
            hours_claimed=hours,
            file_name="ingested.txt",
        )

    def calculate_pay(self, timesheet: Timesheet, user_rate: float) -> PayrollRecord:
        _ = PrivacyVault.scrub_pii(timesheet.raw_text)
        self._last_hours_claimed = timesheet.hours_claimed
        gross_pay = timesheet.hours_claimed * user_rate
        tax = gross_pay * 0.10
        net_pay = gross_pay - tax
        return PayrollRecord(
            id=str(uuid4()),
            timesheet_id=timesheet.id,
            gross_pay=gross_pay,
            tax=tax,
            net_pay=net_pay,
            status="pending",
            audit_flag=False,
            audit_reason="",
        )

    def audit_transaction(self, payroll_record: PayrollRecord) -> PayrollRecord:
        hours_claimed = self._last_hours_claimed or 0.0
        if hours_claimed > 45:
            payroll_record.audit_flag = True
            payroll_record.audit_reason = (
                "Abnormal overtime detected. Requires human approval."
            )
            payroll_record.status = "needs_review"
        else:
            payroll_record.audit_flag = False
            payroll_record.audit_reason = "Clean"
            payroll_record.status = "approved"
        return payroll_record

    def run_pipeline(self, file_content: str, user_rate: float) -> Dict[str, Any]:
        timesheet = self.extract_data(file_content)
        payroll_record = self.calculate_pay(timesheet, user_rate)
        payroll_record = self.audit_transaction(payroll_record)
        return {
            "timesheet": timesheet.model_dump(),
            "payroll_record": payroll_record.model_dump(),
            "audit": {
                "flag": payroll_record.audit_flag,
                "reason": payroll_record.audit_reason,
            },
        }
