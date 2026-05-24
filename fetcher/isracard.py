from __future__ import annotations

from pathlib import Path

from playwright.async_api import Page

from config.settings import BankCredentials
from fetcher import session
from fetcher.base import BankFetcher

_LOGIN_URL = "https://www.isracard.co.il/"

# TODO: confirm exact post-login URL after inspecting with Isracard access.
_PROTECTED_URL = "https://www.isracard.co.il/benefits/account-info/"

# Substring present in the URL when the session expires and Isracard redirects to login.
# TODO: confirm after inspecting session expiry behaviour.
_LOGIN_MARKER = "/login"


class IsracardFetcher(BankFetcher):
    """Fetcher for Isracard credit card (isracard.co.il).

    Credentials:
        user     — Israeli ID number (תעודת זהות)
        password — last 4 digits of any Isracard card (entered digit by digit)

    Login flow:
        1. Fill ID field and 4 card-digit inputs.
        2. Click "שלח קוד לנייד" → Isracard sends OTP via SMS.
        3. Enter OTP code (TODO: OTP screen not yet inspected).
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

        # The last 4 card digits are split across 4 individual inputs (.otp-digit-input).
        # Fill each input with the corresponding character from credentials.password.
        digit_inputs = page.locator(".otp-digit-input")
        for i, digit in enumerate(self._credentials.password):
            await digit_inputs.nth(i).fill(digit)

        await page.get_by_role("button", name="שלח קוד לנייד").click()

        # TODO: fill in after inspecting the OTP confirmation screen.
        #
        # Expected flow:
        #   otp_input = page.locator('<otp code field selector>')
        #   await otp_input.wait_for(state="visible", timeout=20_000)
        #   code = input("[isracard] enter SMS code: ").strip()
        #   await otp_input.fill(code)
        #   await page.get_by_role("button", name="<confirm button text>").click()
        #   await page.wait_for_url("**" + _PROTECTED_URL + "**")

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
