from __future__ import annotations

import hashlib
import re
from typing import Dict

from pydantic import BaseModel


class UserProfile(BaseModel):
    id: str
    name: str
    role: str
    hourly_rate: float


class Timesheet(BaseModel):
    id: str
    user_id: str
    raw_text: str
    hours_claimed: float
    file_name: str


class PayrollRecord(BaseModel):
    id: str
    timesheet_id: str
    gross_pay: float
    tax: float
    net_pay: float
    status: str
    audit_flag: bool
    audit_reason: str


class PrivacyVault:
    _EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    _PHONE_REGEX = re.compile(r"\+?\d[\d\s\-()]{7,}\d")

    @staticmethod
    def scrub_pii(text: str) -> str:
        scrubbed = PrivacyVault._EMAIL_REGEX.sub("[REDACTED]", text)
        scrubbed = PrivacyVault._PHONE_REGEX.sub("[REDACTED]", scrubbed)
        return scrubbed

    @staticmethod
    def anonymize_user(user: UserProfile) -> Dict[str, object]:
        hash_source = f"{user.id}:{user.name}".encode("utf-8")
        hash_suffix = hashlib.sha256(hash_source).hexdigest()[:4].upper()
        return {
            "id": user.id,
            "name": f"User_{hash_suffix}",
            "role": user.role,
            "hourly_rate": user.hourly_rate,
        }
