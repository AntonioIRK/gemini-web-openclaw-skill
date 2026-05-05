from openclaw_gemini_web.cli import build_parser


def test_smoke_defaults_match_storybook_patience_contract():
    parser = build_parser()
    args = parser.parse_args(["smoke"])
    assert args.timeout_seconds == 600
    assert "robot fox" in args.prompt.lower()
