"""Use the archived implementation to inspect or resume this frozen experiment."""
import sys
from pathlib import Path

experiment = Path(__file__).resolve().parent
sys.path.insert(0, str(experiment / "implementation_snapshot"))
from affective.cli import main

sys.argv = [sys.argv[0], "--out", str(experiment), *sys.argv[1:]]
main()
