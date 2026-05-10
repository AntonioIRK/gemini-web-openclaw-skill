import contextlib

@contextlib.contextmanager
def my_context():
    class Ctx:
        result = None
    ctx = Ctx()
    try:
        yield ctx
    except Exception as e:
        ctx.result = f"Error: {e}"

def foo3():
    with my_context() as ctx:
        raise ValueError("oh no")
        ctx.result = "Success"

    return ctx.result

print(foo3())

def foo4():
    with my_context() as ctx:
        return "Success" # The problem here is that returning directly from within `with` skips returning `ctx.result`

    return ctx.result

print(foo4())
