"""Legacy compatibility shim. Primary runtime lives under openclaw_gemini_web."""

from __future__ import annotations

import importlib
import sys

from openclaw_gemini_web import *  # noqa: F401,F403

_ALIAS_MAP = {
    "openclaw_gemini_storybook.client": "openclaw_gemini_web.client",
    "openclaw_gemini_storybook.cli": "openclaw_gemini_web.cli",
    "openclaw_gemini_storybook.config": "openclaw_gemini_web.config",
    "openclaw_gemini_storybook.diagnostics": "openclaw_gemini_web.diagnostics",
    "openclaw_gemini_storybook.exceptions": "openclaw_gemini_web.exceptions",
    "openclaw_gemini_storybook.models": "openclaw_gemini_web.models",
    "openclaw_gemini_storybook.state": "openclaw_gemini_web.state",
    "openclaw_gemini_storybook.auth": "openclaw_gemini_web.auth",
    "openclaw_gemini_storybook.auth.login_flow": "openclaw_gemini_web.auth.login_flow",
    "openclaw_gemini_storybook.auth.profile": "openclaw_gemini_web.auth.profile",
    "openclaw_gemini_storybook.export": "openclaw_gemini_web.export",
    "openclaw_gemini_storybook.export.pdf_export": "openclaw_gemini_web.export.pdf_export",
    "openclaw_gemini_storybook.export.share_link": "openclaw_gemini_web.export.share_link",
    "openclaw_gemini_storybook.skill": "openclaw_gemini_web.skill",
    "openclaw_gemini_storybook.skill.openclaw_adapter": "openclaw_gemini_web.skill.openclaw_adapter",
    "openclaw_gemini_storybook.web": "openclaw_gemini_web.web",
    "openclaw_gemini_storybook.web.base_runner": "openclaw_gemini_web.web.base_runner",
    "openclaw_gemini_storybook.web.browser": "openclaw_gemini_web.web.browser",
    "openclaw_gemini_storybook.web.chat_image_runner": "openclaw_gemini_web.web.chat_image_runner",
    "openclaw_gemini_storybook.web.selectors": "openclaw_gemini_web.web.selectors",
    "openclaw_gemini_storybook.web.state_machine": "openclaw_gemini_web.web.state_machine",
    "openclaw_gemini_storybook.web.storybook_runner": "openclaw_gemini_web.web.storybook_runner",
}

for legacy_name, new_name in _ALIAS_MAP.items():
    sys.modules[legacy_name] = importlib.import_module(new_name)
