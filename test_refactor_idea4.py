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

def foo5():
    with my_context() as ctx:
        ctx.result = "Success"
    return ctx.result

print(foo5())
