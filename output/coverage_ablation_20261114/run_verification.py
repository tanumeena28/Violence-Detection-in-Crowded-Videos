"""Use the archived GPU verifier while preserving frozen training provenance."""
import sys
from pathlib import Path
experiment = Path(__file__).resolve().parent
if len(sys.argv) < 2 or sys.argv[1] not in ('report-cv', 'compare-coverage'):
    raise SystemExit('Use report-cv or compare-coverage; use run_snapshot.py for summarize-cv.')
sys.path.insert(0, str(experiment / 'verification_snapshot'))
from affective.cli import main
sys.argv = [sys.argv[0], '--out', str(experiment), *sys.argv[1:],
            '--implementation-dir', str(experiment / 'implementation_snapshot' / 'affective'),
            '--verification-device', 'cuda']
main()
