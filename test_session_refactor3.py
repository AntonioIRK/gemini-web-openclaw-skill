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
        self.result = None

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

        # Determine the properties result_class takes.
        import dataclasses
        kwargs = {
            "status": "error",
            "debug_artifacts_path": str(self.diag),
            "error_code": code,
            "error_message": str(exc)
        }

        if dataclasses.is_dataclass(self.result_class):
            fields = {f.name for f in dataclasses.fields(self.result_class)}
            if "page_url" in fields:
                kwargs["page_url"] = getattr(self.page, "url", None)
            if "metadata" in fields and self.runtime_meta:
                kwargs["metadata"] = self.runtime_meta
        else:
            kwargs["page_url"] = getattr(self.page, "url", None)
            kwargs["metadata"] = self.runtime_meta

        return self.result_class(**kwargs)

import dataclasses
@dataclasses.dataclass
class GeminiWebResult:
    status: str
    page_url: str = None
    debug_artifacts_path: str = None
    error_code: str = None
    error_message: str = None
    metadata: dict = None

@dataclasses.dataclass
class GeminiWebCreateResult:
    status: str
    debug_artifacts_path: str = None
    error_code: str = None
    error_message: str = None
    metadata: dict = None

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
                    if hasattr(self, "_write_run_summary"):
                        self._write_run_summary(session.diag, "error", session.runtime_meta, error_code=exc.code, error_message=str(exc))
                except Exception as exc:
                    session.result = session.build_error_result(exc, "UNKNOWN_RUNTIME_ERROR")
                    if hasattr(self, "_write_run_summary"):
                        self._write_run_summary(session.diag, "error", session.runtime_meta, error_code="UNKNOWN_RUNTIME_ERROR", error_message=str(exc))
        finally:
            pass

class MyRunner(BaseRunner):
    def test_method(self):
        with self._workflow_session(GeminiWebResult) as session:
            raise ValueError("Something bad happened")
        return session.result

    def test_method2(self):
        with self._workflow_session(GeminiWebCreateResult) as session:
            session.runtime_meta["foo"] = "bar"
            raise GeminiWebError("Known error")
        return session.result

    def _write_run_summary(self, diag, status, meta, **kwargs):
        print(f"Summary: {status} {meta} {kwargs}")

runner = MyRunner()
print(runner.test_method())
print(runner.test_method2())
