import sys
from pathlib import Path
e=Path(__file__).resolve().parent
sys.path.insert(0,str(e/"implementation_snapshot"))
from scripts.run_rwf_finetune import main
if __name__ == "__main__":
    sys.argv=[sys.argv[0],"--out",str(e),*sys.argv[1:]]
    main()
