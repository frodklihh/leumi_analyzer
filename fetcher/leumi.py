from __future__ import annotations

from pathlib import Path

from playwright.async_api import Page

from config.settings import BankCredentials
from fetcher import session
from fetcher.base import BankFetcher

_LOGIN_URL = "https://hb2.bankleumi.co.il"

# URL that is only reachable when authenticated.
# TODO: confirm exact URL after inspecting post-login navigation.
_PROTECTED_URL = "https://hb2.bankleumi.co.il/home"

# Substring that appears in the URL when the bank redirects to the login page.
_LOGIN_MARKER = "gate-keeper"


class LeumiAccountFetcher(BankFetcher):
    name = "leumi_bank"

    def __init__(self, credentials: BankCredentials) -> None:
        self._credentials = credentials

    async def login(self, page: Page) -> None:
        if await session.is_authenticated(page, _PROTECTED_URL, _LOGIN_MARKER):
            print("[leumi] session valid — skipping login")
            return

        print("[leumi] logging in...")
        await page.goto(_LOGIN_URL, wait_until="networkidle")

        await page.locator('[name="user"]').fill(self._credentials.user)
        await page.locator('[name="password"]').fill(self._credentials.password)
        await page.get_by_role("button", name="כניסה לחשבון").click()

        # TODO: fill in after inspecting the OTP screen with Leumi access.
        #
        # Expected flow:
        #   otp_input = page.locator('<selector>')
        #   await otp_input.wait_for(state="visible", timeout=20_000)
        #   code = input("[leumi] enter SMS code: ").strip()
        #   await otp_input.fill(code)
        #   await page.get_by_role("button", name="<confirm button text>").click()
        #   await page.wait_for_url("**" + _PROTECTED_URL + "**")

        print("[leumi] login complete")

    async def download_statement(
        self,
        page: Page,
        year: int,
        month: int,
        dest: Path,
    ) -> list[Path]:
        # TODO: fill in after inspecting the statements export section.
        #
        # Expected flow:
        #   1. Navigate to account movements / export page.
        #   2. Set the date range: use period.billing_month() to compute
        #      the 16th-based start/end dates for the requested month.
        #   3. Select Excel export format.
        #   4. Intercept the download:
        #
        #       async with page.expect_download() as dl_info:
        #           await page.get_by_role("button", name="<export button>").click()
        #       download = await dl_info.value
        #       out = dest / download.suggested_filename
        #       await download.save_as(out)
        #       return [out]

        raise NotImplementedError(
            "LeumiAccountFetcher.download_statement is not implemented yet.\n"
            "Open the bank statement export page and inspect the selectors first."
        )
