import contextlib
from typing import Any

class WorkflowContext:
    def __init__(self, diag: Any, machine: Any, console_lines: list[str]):
        self.diag = diag
        self.machine = machine
        self.console_lines = console_lines
        self.page = None
        self.result = None

@contextlib.contextmanager
def my_context():
    yield WorkflowContext(None, None, [])

def foo():
    with my_context() as ctx:
        ctx.result = "Success!"
        return ctx.result

    return ctx.result # This will actually never run if there is a return inside the 'with' block

print(foo())

def foo2():
    with my_context() as ctx:
        raise ValueError("oh no")
        ctx.result = "Success"

    return ctx.result

try:
    print(foo2())
except Exception as e:
    print(f"Caught {e}")
