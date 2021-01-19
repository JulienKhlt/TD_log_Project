import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path("..").resolve()))
sys.path.insert(0, str(Path("../..").resolve()))

from src.lsp.server import ponthon

logging.basicConfig(filename="ponthon.log", filemode="w", level=logging.DEBUG)
ponthon.start_io()
