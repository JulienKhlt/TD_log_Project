from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from src.bdd.Definition import Definition
from src.bdd.bdd import Base


class Function(Definition):
    __tablename__ = None

    __mapper_args__ = {
        'polymorphic_identity': 'function'
    }
