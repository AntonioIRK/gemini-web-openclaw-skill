with open("src/openclaw_gemini_web/web/base_runner.py", "r") as f:
    content = f.read()

import re
content = re.sub(r"                last_error = True\n", "", content)

with open("src/openclaw_gemini_web/web/base_runner.py", "w") as f:
    f.write(content)
