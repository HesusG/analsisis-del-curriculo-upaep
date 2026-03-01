"""Shared fixtures for docker-deploy tests."""

import sys
from pathlib import Path

# Ensure docker-deploy is on sys.path so imports like `evaluation.schema` work.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
