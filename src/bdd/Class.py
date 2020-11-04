from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from bdd.Definition import Definition
from bdd.bdd import Base


class Class(Definition):
    __tablename__ = None

    __mapper_args__ = {
        'polymorphic_identity': 'class'
    }

