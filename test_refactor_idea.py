import contextlib

@contextlib.contextmanager
def workflow_runner(self):
    diag = self.diagnostics.create()
    machine = GeminiWebStateMachine()
    console_lines: list[str] = []

    class WorkflowContext:
        def __init__(self, diag, machine, console_lines):
            self.diag = diag
            self.machine = machine
            self.console_lines = console_lines
            self.page = None

    ctx = WorkflowContext(diag, machine, console_lines)

    try:
        with open_persistent_page(self.config) as (_context, page):
            ctx.page = page
            page.on("console", lambda msg: console_lines.append(f"{msg.type}: {msg.text}"))
            yield ctx

    except GeminiWebError as exc:
        machine.advance(WorkflowState.FAILED)
        self.diagnostics.write_state(diag, machine.current)
        self._capture_error_context(diag, ctx.page, machine, exc)
        self.diagnostics.write_console(diag, console_lines)
        self.diagnostics.write_json(diag, "error.json", self._error_payload(ctx.page, machine, exc.code, str(exc)))
        ctx.result = GeminiWebResult(status="error", debug_artifacts_path=str(diag.run_dir), error_code=exc.code, error_message=str(exc), page_url=getattr(ctx.page, "url", None))
    except Exception as exc:
        machine.advance(WorkflowState.FAILED)
        self.diagnostics.write_state(diag, machine.current)
        self._capture_error_context(diag, ctx.page, machine, exc)
        self.diagnostics.write_console(diag, console_lines)
        self.diagnostics.write_json(diag, "error.json", self._error_payload(ctx.page, machine, "UNKNOWN_RUNTIME_ERROR", str(exc)))
        ctx.result = GeminiWebResult(status="error", debug_artifacts_path=str(diag.run_dir), error_code="UNKNOWN_RUNTIME_ERROR", error_message=str(exc), page_url=getattr(ctx.page, "url", None))
