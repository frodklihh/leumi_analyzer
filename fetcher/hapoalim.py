from __future__ import annotations

from pathlib import Path

from playwright.async_api import Page

from config.settings import BankCredentials
from fetcher import session
from fetcher.base import BankFetcher

_LOGIN_URL = "https://digital.bankhapoalim.co.il/"
_PROTECTED_URL = "https://login.bankhapoalim.co.il/ng-portals/rb/he/homepage"

# When the session expires Hapoalim redirects back to digital.bankhapoalim.co.il.
# This domain substring is present in the login page URL but not in authenticated URLs.
_LOGIN_MARKER = "digital.bankhapoalim"


class HapoalimFetcher(BankFetcher):
    """Fetcher for Bank Hapoalim (bankhapoalim.co.il).

    Credentials:
        user     — online banking username (קוד משתמש)
        password — online banking password
    """

    name = "hapoalim"

    def __init__(self, credentials: BankCredentials) -> None:
        self._credentials = credentials

    async def login(self, page: Page) -> None:
        if await session.is_authenticated(page, _PROTECTED_URL, _LOGIN_MARKER):
            print("[hapoalim] session valid — skipping login")
            return

        print("[hapoalim] logging in...")
        await page.goto(_LOGIN_URL, wait_until="networkidle")

        await page.locator("#userCode").fill(self._credentials.user)
        await page.locator("#password").fill(self._credentials.password)
        await page.get_by_role("button", name="כניסה").click()

        await page.wait_for_url(f"**{_PROTECTED_URL}**", timeout=15_000)
        print("[hapoalim] login complete")

    async def download_statement(
        self,
        page: Page,
        year: int,
        month: int,
        dest: Path,
    ) -> list[Path]:
        # TODO: fill in after inspecting the Hapoalim statement export UI.
        #
        # Expected flow:
        #   1. Navigate to account movements / export page.
        #   2. Set the date range for the requested billing month.
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
            "HapoalimFetcher.download_statement is not implemented yet."
        )
