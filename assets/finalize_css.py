"""Ensure the built stylesheet ends with a newline.

`tailwindcss --minify` writes its output without a trailing newline, which the repo's
end-of-file-fixer hook then adds back. Left alone, every stylesheet rebuild produces a file
that pre-commit immediately modifies, and a CI run that fails on a freshly built artifact.

Run by `npm run build:css` (as its `post` step).
"""

import pathlib

STYLESHEET = pathlib.Path(__file__).parent.parent / "dac" / "static" / "css" / "dac.css"

content = STYLESHEET.read_bytes()
if not content.endswith(b"\n"):
    STYLESHEET.write_bytes(content + b"\n")
    print(f"added trailing newline to {STYLESHEET.name}")
