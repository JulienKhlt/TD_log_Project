import re
from pathlib import Path

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from bdd.Module import Module
from bdd.bdd import Base, Session
from bdd.Config import Config
from parser.tools import calculate, get_relative_path


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)

    name = Column(String(50))
    path = Column(String(200))

    active = Column(Boolean)
    version = Column(String(20), default="TBD")
    external = Column(Boolean, default=False)
    onedir = Column(Boolean, default=False)

    config = relationship("Config", uselist=False, back_populates="project", cascade="all, delete, delete-orphan")
    module = relationship("Module", back_populates="project", cascade="all, delete, delete-orphan")

    def add_module(self, module_path):
        """Add module to project."""

        # Check if module is not in project.
        if module_path.stem == '__init__':
            module = Module(path=str(module_path.parent), name=module_path.stem)
        else:
            module = Module(path=str(module_path), name=module_path.stem)
        # Reference module
        calculate(module)

        # Add module
        self.module.append(module)

    def get_relative_path(self, fullpath):
        return get_relative_path(self.path, fullpath)

    def get_project_module_search_path(self):
        pass

    def bind_imports(self, session=Session()):
        """Bind modules together via imports. Call this AFTER all modules have been indexed."""
        for project_module in self.module:
            for module_import in project_module.imports:
                paths = self.config.get_python_module_search_path()
                formated_module_name = '/'.join(module_import.name.split('.'))
                for string_path in paths:
                    path = Path(string_path, formated_module_name)

                    # result = session.query(Module.id).filter_by(path='/usr/lib/python3.8/unittest').first()
                    result = session.query(Module.id).filter(Module.path.op('regexp')(str(path) + r'?\.py')).first()
                    if result:
                        module_import.module_to_id = result[0]
                        break
                if not module_import.module_to_id:
                    print(f"Import not found: {module_import.name}")
                    pass
        session.commit()


