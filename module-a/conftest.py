"""Make the local `greetings` package importable when pytest targets module-a/.

The project's package discovery in pyproject.toml only covers `src/`, so this
directory is not on sys.path by default. Adding it here keeps module-a
self-contained without touching the root packaging config.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
