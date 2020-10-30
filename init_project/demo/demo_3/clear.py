import sys
from pathlib import Path

sys.path.extend(['../../src'])

from find_project import *

clear_project()
init_project(path=Path().resolve() / 'subdirectory_1')
