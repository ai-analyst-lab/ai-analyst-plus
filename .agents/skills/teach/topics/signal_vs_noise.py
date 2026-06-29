"""Compatibility wrapper for the shared signal-vs-noise teaching topic.

Outputs remain under outputs/charts/teach/signal-vs-noise/.
"""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[4]
SHARED_TOPIC = ROOT / "shared" / "teach" / "topics" / "signal_vs_noise.py"


def main():
    """Run the shared signal-vs-noise topic implementation."""
    runpy.run_path(str(SHARED_TOPIC), run_name="__main__")


if __name__ == "__main__":
    main()
