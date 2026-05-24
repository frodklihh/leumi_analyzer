from __future__ import annotations

from pathlib import Path

from playwright.async_api import Page

from config.settings import BankCredentials
from fetcher import session
from fetcher.base import BankFetcher

_LOGIN_URL = "https://www.isracard.co.il/"

# TODO: confirm post-login URL and login redirect marker after inspecting with Isracard access.
_PROTECTED_URL = "https://www.isracard.co.il/benefits/account-info/"
_LOGIN_MARKER = "/login"


class IsracardFetcher(BankFetcher):
    """Fetcher for Isracard credit card (isracard.co.il).

    Credentials:
        user     — Israeli ID number (תעודת זהות)
        password — TODO: confirm what Isracard uses as second factor
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

        # TODO: fill in after inspecting the Isracard login form.
        #
        # Expected flow (typical for Israeli card sites):
        #   await page.locator('<id field selector>').fill(self._credentials.user)
        #   await page.locator('<password field selector>').fill(self._credentials.password)
        #   await page.get_by_role("button", name="<login button text>").click()
        #
        #   otp_input = page.locator('<otp field selector>')
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
