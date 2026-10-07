#!/usr/bin/env python3
"""Verify the canonical MIGRATION display (generic checker)."""
import sys
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
try:
    sys.exit(subprocess.call([str(ROOT/"scripts/check_canonical_display.py"), 'MIGRATION']))
except KeyboardInterrupt:
    sys.exit(130)
