from __future__ import annotations

from pathlib import Path

from playwright.async_api import Page

from config.settings import BankCredentials
from fetcher import session
from fetcher.base import BankFetcher

_LOGIN_URL = "https://www.cal-online.co.il/"

# TODO: confirm the exact post-login URL after inspecting with Cal access.
_PROTECTED_URL = "https://www.cal-online.co.il/he/account"

# Substring that appears in the URL when the session expires and Cal redirects to login.
# TODO: confirm after inspecting with Cal access.
_LOGIN_MARKER = "/login"

# We always request OTP via SMS. To support WhatsApp or phone call,
# change this to the matching button text.
_OTP_METHOD_BUTTON = "שלחו לי סיסמה ב-SMS"


class CalCardFetcher(BankFetcher):
    """Fetcher for Cal credit card (cal-online.co.il).

    Credentials:
        user     — Israeli ID number (תעודת זהות)
        password — last 4 digits of any Cal card
    """

    name = "cal_card"

    def __init__(self, credentials: BankCredentials) -> None:
        self._credentials = credentials

    async def login(self, page: Page) -> None:
        if await session.is_authenticated(page, _PROTECTED_URL, _LOGIN_MARKER):
            print("[cal] session valid — skipping login")
            return

        print("[cal] logging in...")
        await page.goto(_LOGIN_URL, wait_until="networkidle")

        await page.locator('[formcontrolname="id"]').fill(self._credentials.user)
        await page.locator('[formcontrolname="secondOtpParam"]').fill(self._credentials.password)

        # Clicking this button both submits the form and triggers OTP delivery via SMS.
        await page.get_by_role("button", name=_OTP_METHOD_BUTTON).click()

        # TODO: fill in after inspecting the OTP screen with Cal access.
        #
        # Expected flow:
        #   otp_input = page.locator('<selector>')
        #   await otp_input.wait_for(state="visible", timeout=20_000)
        #   code = input("[cal] enter SMS code: ").strip()
        #   await otp_input.fill(code)
        #   await page.get_by_role("button", name="<confirm button text>").click()
        #   await page.wait_for_url("**" + _PROTECTED_URL + "**")

        print("[cal] login complete")

    async def download_statement(
        self,
        page: Page,
        year: int,
        month: int,
        dest: Path,
    ) -> list[Path]:
        # TODO: fill in after inspecting the Cal statement export UI.
        #
        # Expected flow:
        #   1. Navigate to the transactions / export section.
        #   2. Set the billing month date range.
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
            "CalCardFetcher.download_statement is not implemented yet.\n"
            "Open the Cal statement export page and inspect the selectors first."
        )
