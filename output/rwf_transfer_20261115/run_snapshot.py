import sys
from pathlib import Path
experiment = Path(__file__).resolve().parent
sys.path.insert(0, str(experiment / "implementation_snapshot"))
from scripts.evaluate_rwf_transfer import main
sys.argv = [sys.argv[0], "--root", str(experiment.parents[1]), "--out", str(experiment), *sys.argv[1:]]
main()
