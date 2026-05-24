from __future__ import annotations

from pathlib import Path

from playwright.async_api import Page

from config.settings import BankCredentials
from fetcher import session
from fetcher.base import BankFetcher

_LOGIN_URL = "https://www.isracard.co.il/"
_PROTECTED_URL = "https://web.isracard.co.il/StatusPage"

# When the session expires Isracard redirects back to www.isracard.co.il.
# This subdomain is present in the login-page URL but absent in authenticated URLs
# (which live under web.isracard.co.il).
_LOGIN_MARKER = "www.isracard.co.il"


class IsracardFetcher(BankFetcher):
    """Fetcher for Isracard credit card (isracard.co.il).

    Credentials:
        user     — Israeli ID number (תעודת זהות)
        password — last 4 digits of any Isracard card (entered digit by digit)

    Login flow:
        1. Fill ID + 4 card-digit inputs → click "שלח קוד לנייד" (send SMS OTP).
        2. Enter the 6-digit SMS code → click "כניסה לחשבון שלי" (confirm).
    """

    name = "isracard"

    def __init__(self, credentials: BankCredentials) -> None:
        self._credentials = credentials

    async def login(self, page: Page) -> None:
        if await session.is_authenticated(page, _PROTECTED_URL, _LOGIN_MARKER):
            print("[isracard] session valid — skipping login")
            return

        print("[isracard] logging in...")
        await page.goto(_LOGIN_URL, wait_until="networkidle")

        await page.locator("#otpLoginId_SMS").fill(self._credentials.user)

        # The last 4 card digits are split across 4 individual inputs.
        digit_inputs = page.locator(".otp-digit-input")
        for i, digit in enumerate(self._credentials.password):
            await digit_inputs.nth(i).fill(digit)

        await page.get_by_role("button", name="שלח קוד לנייד").click()

        otp_input = page.locator("#otpInput")
        await otp_input.wait_for(state="visible", timeout=20_000)
        code = input("[isracard] enter SMS code: ").strip()
        await otp_input.fill(code)

        await page.get_by_role("button", name="כניסה לחשבון שלי").click()
        await page.wait_for_url(f"**{_PROTECTED_URL}**", timeout=15_000)

        print("[isracard] login complete")

    async def download_statement(
        self,
        page: Page,
        year: int,
        month: int,
        dest: Path,
    ) -> list[Path]:
        # TODO: fill in after inspecting the Isracard statement export UI.
        raise NotImplementedError(
            "IsracardFetcher.download_statement is not implemented yet."
        )
