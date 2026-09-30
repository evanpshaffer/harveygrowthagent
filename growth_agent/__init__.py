"""Growth Agent prototype: integration layer, analysis engine, guardrails and reasoning layer."""
import sys

if sys.version_info < (3, 10):
    raise SystemExit(
        "Growth Agent needs Python 3.10 or newer. This is Python %d.%d.\n"
        "Create the virtual environment with a newer Python, for example: uv venv --python 3.12"
        % sys.version_info[:2]
    )

__version__ = "0.2.0"
