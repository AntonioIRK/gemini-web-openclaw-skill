from __future__ import annotations

import argparse
import json

from .models import GeminiImageRequest, GeminiWebCreateRequest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gemini-web-skill")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("login")
    sub.add_parser("doctor")
    sub.add_parser("debug-open")
    sub.add_parser("inspect-home")

    smoke = sub.add_parser("smoke")
    smoke.add_argument("--prompt", default="Create a very short 3-scene bedtime story about a tiny robot fox learning to share.")
    smoke.add_argument("--timeout-seconds", type=int, default=600)

    image = sub.add_parser("image-create")
    image.add_argument("--prompt", required=True)
    image.add_argument("--file", dest="files", action="append", default=[])
    image.add_argument("--timeout-seconds", type=int, default=120)
    image.add_argument("--new-thread", action="store_true")

    edit = sub.add_parser("image-edit")
    edit.add_argument("--prompt", required=True)
    edit.add_argument("--file", dest="files", action="append", default=[])
    edit.add_argument("--timeout-seconds", type=int, default=120)
    edit.add_argument("--new-thread", action="store_true")

    chat = sub.add_parser("chat-ask")
    chat.add_argument("--prompt", required=True)
    chat.add_argument("--timeout-seconds", type=int, default=120)
    chat.add_argument("--new-thread", action="store_true")

    create = sub.add_parser("create")
    create.add_argument("--prompt", required=True)
    create.add_argument("--file", dest="files", action="append", default=[])
    create.add_argument("--return-mode", choices=["share_link", "pdf"], default="share_link")
    create.add_argument("--output")
    create.add_argument("--timeout-seconds", type=int, default=300)
    create.add_argument("--debug", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    from .client import GeminiWebClient

    client = GeminiWebClient()

    if args.command == "login":
        client.login()
        return 0
    if args.command == "doctor":
        print(json.dumps(client.doctor(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "debug-open":
        client.debug_open()
        return 0
    if args.command == "inspect-home":
        print(json.dumps(client.inspect_home(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "smoke":
        request = GeminiWebCreateRequest(
            prompt=args.prompt,
            return_mode="share_link",
            timeout_seconds=args.timeout_seconds,
            debug=True,
        )
        result = client.create(request)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.status == "success" else 1
    if args.command == "image-create":
        request = GeminiImageRequest(
            prompt=args.prompt,
            files=args.files,
            timeout_seconds=args.timeout_seconds,
            new_thread=args.new_thread,
            mode="image-create",
        )
        result = client.create_image(request)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.status == "success" else 1
    if args.command == "image-edit":
        request = GeminiImageRequest(
            prompt=args.prompt,
            files=args.files,
            timeout_seconds=args.timeout_seconds,
            new_thread=args.new_thread,
            mode="image-edit",
        )
        result = client.create_image(request)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.status == "success" else 1
    if args.command == "chat-ask":
        result = client.ask_chat(prompt=args.prompt, timeout_seconds=args.timeout_seconds, new_thread=args.new_thread)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.status == "success" else 1
    if args.command == "create":
        request = GeminiWebCreateRequest(
            prompt=args.prompt,
            files=args.files,
            return_mode=args.return_mode,
            output_path=args.output,
            timeout_seconds=args.timeout_seconds,
            debug=args.debug,
        )
        result = client.create(request)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.status == "success" else 1

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
