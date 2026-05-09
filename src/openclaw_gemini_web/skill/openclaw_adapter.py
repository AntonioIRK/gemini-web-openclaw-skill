from __future__ import annotations

from ..models import GeminiImageRequest, GeminiWebCreateRequest


from typing import Any

def run_openclaw_skill(payload: dict) -> dict | Any:
    from ..client import GeminiWebClient
    mode = payload.get("mode", "create")
    client = GeminiWebClient()

    if mode == "chat-ask":
        return client.ask_chat(
            prompt=payload["prompt"],
            timeout_seconds=int(payload.get("timeout_seconds", 120)),
            new_thread=bool(payload.get("new_thread", False)),
        ).to_dict()

    if mode == "chat-ask-stream":
        # Returns a generator yielding strings
        return client.ask_chat_stream(
            prompt=payload["prompt"],
            timeout_seconds=int(payload.get("timeout_seconds", 120)),
            new_thread=bool(payload.get("new_thread", False)),
        )

    if mode in {"image-create", "image-edit", "document-analysis"}:
        request = GeminiImageRequest(
            prompt=payload["prompt"],
            files=payload.get("files", []),
            timeout_seconds=int(payload.get("timeout_seconds", 300)),
            new_thread=bool(payload.get("new_thread", False)),
            mode=mode,
        )
        return client.create_image(request).to_dict()

    request = GeminiWebCreateRequest(
        prompt=payload["prompt"],
        files=payload.get("files", []),
        return_mode=payload.get("return_mode", "share_link"),
        output_path=payload.get("output_path"),
        timeout_seconds=int(payload.get("timeout_seconds", 300)),
        debug=bool(payload.get("debug", False)),
    )
    return client.create(request).to_dict()
