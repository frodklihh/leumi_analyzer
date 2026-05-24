from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class BankCredentials:
    user: str
    password: str


@dataclass(frozen=True)
class EmailConfig:
    host: str
    port: int
    user: str
    password: str
    sender: str
    recipient: str


def _require(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise EnvironmentError(f"Missing required env var: {key}")
    return value


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def leumi_credentials() -> BankCredentials:
    return BankCredentials(
        user=_require("LEUMI_USER"),
        password=_require("LEUMI_PASSWORD"),
    )


def cal_credentials() -> BankCredentials:
    return BankCredentials(
        user=_require("CAL_USER"),
        password=_require("CAL_PASSWORD"),
    )


def email_config() -> EmailConfig:
    return EmailConfig(
        host=_optional("SMTP_HOST", "smtp.gmail.com"),
        port=int(_optional("SMTP_PORT", "587")),
        user=_require("SMTP_USER"),
        password=_require("SMTP_PASSWORD"),
        sender=_optional("EMAIL_FROM") or _require("SMTP_USER"),
        recipient=_require("EMAIL_TO"),
    )


SESSION_DIR = Path.home() / ".leumi_analyzer" / "sessions"
