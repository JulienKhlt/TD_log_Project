import subprocess
import sys
import pkg_resources
from pathlib import PurePath, Path

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from bdd.bdd import Base


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)

    python_home = Column(String(200), default=sys.prefix)
    ignore_dirs = Column(String(200))
    ignore_files = Column(String(200))
    version_control = Column(Boolean, default=False)

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
        """Return a list of PurePath which contains where python will look for modules."""

        script = "import sys;print(sys.path)"
        # script = "import sys;print(sys.prefix)"
        python_path = self.get_python_exec()
        output = subprocess.check_output([str(python_path), "-c", script])

        return eval(output)
        # return output
