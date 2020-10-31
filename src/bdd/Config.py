from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from bdd.bdd import Base


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)

    python_home = Column(String(200))
    ignore_dirs = Column(String(200))
    ignore_files = Column(String(200))
    version_control = Column(Boolean)

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="config")

