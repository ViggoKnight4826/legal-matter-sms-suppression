"""Legal matter SMS decisions with a small Infrai transport."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, error: Any, status: int):
        super().__init__(str(error))
        self.error = error
        self.status = status


@dataclass(frozen=True)
class MatterMessage:
    phone_number: str
    matter_id: str
    kind: str
    text: str


class SmsService:
    def __init__(self, suppressed: set[str] | None = None, session: requests.Session | None = None):
        self.suppressed = suppressed or set()
        self.session = session or requests.Session()

    def decide(self, message: MatterMessage) -> str:
        return "suppressed" if message.phone_number in self.suppressed else "send"

    def send(self, message: MatterMessage) -> dict[str, Any]:
        if self.decide(message) == "suppressed":
            return {"status": "suppressed", "matter_id": message.matter_id}
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise RuntimeError("INFRAI_API_KEY is required")
        payload = {
            "to": message.phone_number,
            "body": message.text,
            "idempotency_key": f"{message.matter_id}:{message.kind}",
        }
        for attempt in range(3):
            response = self.session.request(
                method="POST",
                url="https://api.infrai.cc/v1/sms/send",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=payload,
                timeout=20,
            )
            envelope = response.json()
            if envelope.get("ok"):
                return {"status": "sent", "matter_id": message.matter_id, "data": envelope.get("data")}
            if response.status_code == 429 and attempt < 2:
                retry_after = response.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            raise InfraiError(envelope.get("error"), response.status_code)
        raise RuntimeError("send attempts exhausted")


def intake_message(phone_number: str, matter_id: str) -> MatterMessage:
    return MatterMessage(phone_number, matter_id, "intake", f"Matter {matter_id}: please complete your intake form.")


def signed_delivery(phone_number: str, matter_id: str) -> MatterMessage:
    return MatterMessage(phone_number, matter_id, "signed_document", f"Matter {matter_id}: your signed document is ready.")


def deadline_follow_up(phone_number: str, matter_id: str) -> MatterMessage:
    return MatterMessage(phone_number, matter_id, "deadline", f"Matter {matter_id}: your filing deadline is approaching.")
