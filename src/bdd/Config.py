import logging
import subprocess
import sys
import pkg_resources
from pathlib import PurePath, Path

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.bdd.bdd import Base


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)

    python_home = Column(String(200), default=sys.prefix)
    ignore_dirs = Column(String(200))
    ignore_files = Column(String(200))
    version_control = Column(Boolean, default=False)

    # Does not import all bound project anymore, just necessary modules.
    fast = Column(Boolean, default=True)

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="config")

    def get_python_exec(self):
        """Return PurePath with location of project's python executable."""
        return Path(self.python_home, 'bin/python')

    def get_version(self, child):
        try:
            return str(pkg_resources.get_distribution(child.name))
        except:
            return None

    def get_python_module_search_path(self):
        """Return a list of Path which contains where python will look for modules."""

        script = "import sys;print(sys.path)"
        python_path = self.get_python_exec()
        output = subprocess.check_output([str(python_path), "-c", script])

        string_paths = eval(output)
        paths = [Path(string_path) for string_path in string_paths]

        return paths
