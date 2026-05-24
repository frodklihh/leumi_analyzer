from __future__ import annotations

import json
from pathlib import Path

from playwright.async_api import BrowserContext, Page

from config.settings import SESSION_DIR


def _session_path(name: str) -> Path:
    return SESSION_DIR / f"{name}.json"


async def load(ctx: BrowserContext, name: str) -> bool:
    """Load saved cookies into the browser context.

    Returns True if a session file was found and loaded, False otherwise.
    """
    path = _session_path(name)
    if not path.exists():
        return False
    state = json.loads(path.read_text(encoding="utf-8"))
    await ctx.add_cookies(state.get("cookies", []))
    return True


async def save(ctx: BrowserContext, name: str) -> None:
    """Persist the current browser context cookies to disk."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    state = await ctx.storage_state()
    path = _session_path(name)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


async def is_authenticated(page: Page, protected_url: str, login_marker: str) -> bool:
    """Navigate to a protected URL and check if we are still logged in.

    login_marker is a substring of the URL that the bank redirects to
    when the session has expired (e.g. '/login', '/authenticate').
    Returns False if we ended up on the login page.
    """
    await page.goto(protected_url, wait_until="domcontentloaded")
    return login_marker not in page.url


def clear(name: str) -> None:
    """Delete a saved session file (useful for manual reset)."""
    path = _session_path(name)
    if path.exists():
        path.unlink()
