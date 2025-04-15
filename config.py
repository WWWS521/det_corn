
import os
import sys
from pathlib import Path

file_path = Path(__file__).resolve()
root_path = file_path.parent
if root_path not in sys.path:
    sys.path.append(str(root_path))
ROOT = root_path.relative_to(Path.cwd())
MODEL_DIR = ROOT / 'weights'

MODEL_LIST=[]

weights=os.listdir(MODEL_DIR)

for weight in weights:
    MODEL_LIST.append(weight)