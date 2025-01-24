#!/usr/bin/python3
""" State Module for HBNB project """
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String
import os


class State(BaseModel, Base):
    """ State class """
    __tablename__ = 'states'

    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        name = Column(String(128), nullable=False, default="")
    else:
        name = ""

    def __init__(self, *args, **kwargs):
        """Initialize State instance with default name if not provided"""
        super().__init__(*args, **kwargs)
        if getattr(self, 'name', None) is None:
            self.name = ""
