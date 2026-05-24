from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from playwright.async_api import BrowserContext, Page


class BankFetcher(ABC):
    """Base class for all bank/card fetchers.

    Subclasses implement login() and download_statement().
    The fetch() template method handles the browser lifecycle and session I/O.
    """

    # Override in subclass to give each fetcher a unique session filename.
    name: str = ""

    @abstractmethod
    async def login(self, page: Page) -> None:
        """Authenticate on the bank's website.

        Must handle the case where the session is already valid (no-op)
        and the case where full login + OTP is required.
        Implementations should use input() to prompt for OTP interactively.
        """

    @abstractmethod
    async def download_statement(
        self,
        page: Page,
        year: int,
        month: int,
        dest: Path,
    ) -> list[Path]:
        """Navigate to the export section and download statement file(s).

        Returns the list of downloaded file paths inside dest/.
        """

    async def fetch(
        self,
        ctx: BrowserContext,
        year: int,
        month: int,
        dest: Path,
    ) -> list[Path]:
        """Open a page, log in if needed, download, and return file paths."""
        dest.mkdir(parents=True, exist_ok=True)
        page = await ctx.new_page()
        try:
            await self.login(page)
            return await self.download_statement(page, year, month, dest)
        finally:
            await page.close()
