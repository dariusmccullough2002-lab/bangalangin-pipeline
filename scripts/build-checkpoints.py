"""Compatibility entry point: preserve individually reviewed plans; never regenerate templates."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("rebuild-deep-checkpoints.py")),run_name="__main__")
