from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from bdd.Module import Module
from bdd.bdd import Base
from bdd.Config import Config
from parser.tools import calculate


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)

    name = Column(String(50))
    path = Column(String(200))

    active = Column(Boolean)

    config = relationship("Config", uselist=False, back_populates="project", cascade="all, delete, delete-orphan")
    module = relationship("Module", back_populates="project", cascade="all, delete, delete-orphan")

    def add_module(self, module_path):
        """Add module to project."""

        # Check if module is not in project.

        module = Module(path=str(module_path), name=module_path.stem)
        # Reference module
        calculate(module)

        # Add module
        self.module.append(module)
