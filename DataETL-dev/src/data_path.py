import pathlib
import os 

REPO_PATH = pathlib.Path(__file__).parent.parent.absolute()
SRC_PATH = os.path.join(REPO_PATH, "src")
DATA_PATH = os.path.join(REPO_PATH, "data")
