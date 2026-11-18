import sys
from pathlib import Path
e=Path(__file__).resolve().parent
sys.path.insert(0,str(e/"implementation_snapshot"))
from scripts.evaluate_video_transfer import main
sys.argv=[sys.argv[0],"--out",str(e),*sys.argv[1:]]
main()
