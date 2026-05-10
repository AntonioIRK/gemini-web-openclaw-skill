import contextlib

@contextlib.contextmanager
def workflow_session(runner, request_type=None):
    class WorkflowSession:
        def __init__(self):
            self.diag = runner.diagnostics.create()
            self.machine = GeminiWebStateMachine()
            self.console_lines = []
            self.page = None
            self.runtime_meta = {}
            self.result = None

        def build_error_result(self, exc, is_unknown=False):
            code = "UNKNOWN_RUNTIME_ERROR" if is_unknown else getattr(exc, "code", "UNKNOWN_RUNTIME_ERROR")

            self.machine.advance(WorkflowState.FAILED)
            self.runtime_meta["final_page_url"] = getattr(self.page, "url", None)
            self.runtime_meta["error_code"] = code

            runner.diagnostics.write_state(self.diag, self.machine.current, self.runtime_meta)
            runner._capture_error_context(self.diag, self.page, self.machine, exc)
            runner.diagnostics.write_console(self.diag, self.console_lines)

            payload = runner._error_payload(self.page, self.machine, code, str(exc))
            if self.runtime_meta:
                payload["metadata"] = self.runtime_meta
            runner.diagnostics.write_json(self.diag, "error.json", payload)

            # How to return different result classes?
            # We can use request_type parameter or duck typing

    session = WorkflowSession()

    try:
        with open_persistent_page(runner.config) as (_context, page):
            session.page = page
            page.on("console", lambda msg: session.console_lines.append(f"{msg.type}: {msg.text}"))
            yield session

    except GeminiWebError as exc:
        session.build_error_result(exc, is_unknown=False)
    except Exception as exc:
        session.build_error_result(exc, is_unknown=True)
