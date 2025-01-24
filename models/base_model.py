#!/usr/bin/python3
"""This module defines a base class for all models in our hbnb clone"""
import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
import os

Base = declarative_base()


class BaseModel:
    """A base class for all hbnb models"""
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        id = Column(String(60), primary_key=True, nullable=False)
        created_at = Column(DateTime, default=datetime.now, nullable=False)
        updated_at = Column(DateTime, default=datetime.now, nullable=False)

    def __init__(self, *args, **kwargs):
        """Instantiates a new model"""
        # Initialize default attributes if no kwargs are provided
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        if kwargs:
            # Define valid attributes for BaseModel
            valid_attrs = ['id', 'created_at', 'updated_at', '__class__']
            if hasattr(self.__class__, '__table__'):
                valid_attrs.extend([col.name for col in self.__class__.__table__.columns])

            # Check for invalid attributes
            invalid_keys = [key for key in kwargs if key not in valid_attrs]
            if invalid_keys:
                raise KeyError(f"Invalid attribute(s): {', '.join(invalid_keys)}")

            # Convert datetime strings to datetime objects if needed
            if 'created_at' in kwargs and isinstance(kwargs['created_at'], str):
                kwargs['created_at'] = datetime.strptime(kwargs['created_at'], '%Y-%m-%dT%H:%M:%S.%f')
            if 'updated_at' in kwargs and isinstance(kwargs['updated_at'], str):
                kwargs['updated_at'] = datetime.strptime(kwargs['updated_at'], '%Y-%m-%dT%H:%M:%S.%f')

            # Assign attributes from kwargs
            for key, value in kwargs.items():
                if key != '__class__':
                    setattr(self, key, value)

    def __str__(self):
        """Returns a string representation of the instance"""
        cls = (str(type(self)).split('.')[-1]).split('\'')[0]
        return f'[{cls}] ({self.id}) {self.__dict__}'

    def save(self):
        """Updates updated_at with current time when instance is changed"""
        from models import storage
        self.updated_at = datetime.now()
        storage.save()

    def to_dict(self):
        """Convert instance into dict format"""
        dictionary = self.__dict__.copy()
        dictionary.pop('_sa_instance_state', None)  # Remove SQLAlchemy state if present

        # Add class name for identifying class
        dictionary['__class__'] = self.__class__.__name__
        dictionary['created_at'] = self.created_at.isoformat()
        dictionary['updated_at'] = self.updated_at.isoformat()

        # Handle dynamic class ID in dictionary
        class_name = self.__class__.__name__
        dictionary[f"{class_name}.{self.id}"] = dictionary

        return dictionary
