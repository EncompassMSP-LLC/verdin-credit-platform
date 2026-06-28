"""Run mypy for the API package (used by pre-commit)."""

import subprocess
import sys
from pathlib import Path

api_dir = Path(__file__).resolve().parents[2] / "apps" / "api"

raise SystemExit(
    subprocess.call(
        [sys.executable, "-m", "mypy", "--config-file=pyproject.toml", "api", "main.py"],
        cwd=api_dir,
    )
)
