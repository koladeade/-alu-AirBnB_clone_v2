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
        if not kwargs:
            from models import storage
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
            storage.new(self)
        else:
            # Assign default or passed values to attributes
            self.id = kwargs.pop('id', str(uuid.uuid4()))
            self.created_at = kwargs.pop('created_at', datetime.now())
            self.updated_at = kwargs.pop('updated_at', datetime.now())

            # Convert datetime strings to datetime objects if needed
            if isinstance(self.created_at, str):
                self.created_at = datetime.strptime(
                    self.created_at, '%Y-%m-%dT%H:%M:%S.%f'
                )
            if isinstance(self.updated_at, str):
                self.updated_at = datetime.strptime(
                    self.updated_at, '%Y-%m-%dT%H:%M:%S.%f'
                )

            # Validate attributes only for DBStorage and mapped subclasses
            if os.getenv('HBNB_TYPE_STORAGE') == 'db' and hasattr(self.__class__, '__table__'):
                valid_attrs = {'id', 'created_at', 'updated_at', '__class__'}
                valid_attrs.update(
                    col.name for col in self.__class__.__table__.columns
                )
                valid_attrs.add('_sa_instance_state')  # SQLAlchemy internal state

                invalid_keys = [k for k in kwargs if k not in valid_attrs]
                if invalid_keys:
                    error_msg = (
                        f"Invalid attribute(s): {', '.join(invalid_keys)} "
                        f"for {self.__class__.__name__}"
                    )
                    raise KeyError(error_msg)

            kwargs.pop('__class__', None)  # Remove the `__class__` key
            self.__dict__.update(kwargs)

    def __str__(self):
        """Returns a string representation of the instance"""
        cls = (str(type(self)).split('.')[-1]).split('\'')[0]
        return f'[{cls}] ({self.id}) {self.__dict__}'

    def save(self):
        """Updates `updated_at` with the current time when instance is changed"""
        from models import storage
        self.updated_at = datetime.now()
        storage.save()

    def to_dict(self):
        """Convert instance into dict format"""
        dictionary = self.__dict__.copy()
        dictionary.pop('_sa_instance_state', None)  # Remove SQLAlchemy instance state
        dictionary['__class__'] = self.__class__.__name__
        dictionary['created_at'] = self.created_at.isoformat()
        dictionary['updated_at'] = self.updated_at.isoformat()
        return dictionary

    def delete(self):
        """Deletes the current instance from storage"""
        from models import storage
        storage.delete(self)