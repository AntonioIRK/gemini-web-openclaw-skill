import contextlib

class FakeDiagnostics:
    def create(self): return "diag"
    def write_state(self, diag, state, extra=None): pass
    def write_console(self, diag, console_lines): pass
    def write_json(self, diag, name, payload): pass

class FakeMachine:
    current = "STATE"
    def advance(self, state): pass

class FakePage:
    def __init__(self):
        self.url = "http://example.com"
    def on(self, event, cb): pass

class FakeConfig:
    pass

@contextlib.contextmanager
def open_persistent_page(config):
    yield "context", FakePage()

class GeminiWebError(Exception):
    def __init__(self, msg):
        self.code = "KNOWN_ERROR"
        super().__init__(msg)

class WorkflowSession:
    def __init__(self, runner, result_class):
        self.runner = runner
        self.result_class = result_class
        self.diag = runner.diagnostics.create()
        self.machine = FakeMachine()
        self.console_lines = []
        self.page = None
        self.runtime_meta = {}

    def build_error_result(self, exc, code):
        self.machine.advance("FAILED")
        self.runtime_meta["final_page_url"] = getattr(self.page, "url", None)
        self.runtime_meta["error_code"] = code

        self.runner.diagnostics.write_state(self.diag, self.machine.current, self.runtime_meta)
        self.runner._capture_error_context(self.diag, self.page, self.machine, exc)
        self.runner.diagnostics.write_console(self.diag, self.console_lines)

        payload = self.runner._error_payload(self.page, self.machine, code, str(exc))
        if self.runtime_meta:
            payload["metadata"] = self.runtime_meta
        self.runner.diagnostics.write_json(self.diag, "error.json", payload)

        return self.result_class(
            status="error",
            debug_artifacts_path=str(self.diag),
            error_code=code,
            error_message=str(exc),
            page_url=getattr(self.page, "url", None)
        )

class GeminiWebResult:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class BaseRunner:
    def __init__(self):
        self.diagnostics = FakeDiagnostics()
        self.config = FakeConfig()

    def _capture_error_context(self, diag, page, machine, exc): pass
    def _error_payload(self, page, machine, code, msg): return {"code": code}

    @contextlib.contextmanager
    def _workflow_session(self, result_class):
        session = WorkflowSession(self, result_class)
        try:
            with open_persistent_page(self.config) as (_context, page):
                session.page = page
                page.on("console", lambda msg: session.console_lines.append(f"{msg.type}: {msg.text}"))

                try:
                    yield session
                except GeminiWebError as exc:
                    session.result = session.build_error_result(exc, exc.code)
                except Exception as exc:
                    session.result = session.build_error_result(exc, "UNKNOWN_RUNTIME_ERROR")
        finally:
            pass

class MyRunner(BaseRunner):
    def test_method(self):
        with self._workflow_session(GeminiWebResult) as session:
            # Fake some work
            raise ValueError("Something bad happened")
        return session.result

runner = MyRunner()
print(runner.test_method().kwargs)
