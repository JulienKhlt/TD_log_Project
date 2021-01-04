import sys
from pathlib import Path

sys.path.insert(0, str(Path("..").resolve()))
sys.path.insert(0, str(Path("../..").resolve()))

from src.lsp.server import ponthon

ponthon.start_io()
