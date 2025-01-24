#!/usr/bin/python3
"""Defines the BaseModel class for both FileStorage and DBStorage"""
import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
import os

Base = declarative_base()

class BaseModel:
    """Base class for all models with conditional DBStorage validation"""
    if os.getenv('HBNB_TYPE_STORAGE') == 'db':
        id = Column(String(60), primary_key=True, nullable=False)
        created_at = Column(DateTime, default=datetime.now, nullable=False)
        updated_at = Column(DateTime, default=datetime.now, nullable=False)

    def __init__(self, *args, **kwargs):
        """Initializes model instances with storage-aware validation"""
        self.id = str(uuid.uuid4())
        self.created_at = self.updated_at = datetime.now()
        
        if kwargs:
            self._process_kwargs(kwargs)
            
        # Only call storage.new() if not reloading from storage
        if not kwargs or '__class__' not in kwargs:
            from models import storage
            storage.new(self)

    def _process_kwargs(self, kwargs):
        """Handles keyword arguments with storage-specific validation"""
        kwargs.pop('__class__', None)
        
        # Convert datetime strings for all storage types
        self._convert_datetimes(kwargs)
        
        # DBStorage: Validate attributes for mapped subclasses only
        if os.getenv('HBNB_TYPE_STORAGE') == 'db':
            self._validate_db_attributes(kwargs)
            
        self.__dict__.update(kwargs)

    def _convert_datetimes(self, kwargs):
        """Converts string datetime values to datetime objects"""
        for key in ['created_at', 'updated_at']:
            if key in kwargs and isinstance(kwargs[key], str):
                kwargs[key] = datetime.strptime(
                    kwargs[key], '%Y-%m-%dT%H:%M:%S.%f'
                )

    def _validate_db_attributes(self, kwargs):
        """Validates attributes for DBStorage-mapped subclasses"""
        if hasattr(self.__class__, '__table__'):
            valid_attrs = {
                'id', 'created_at', 'updated_at', 
                '_sa_instance_state', '__class__'
            }
            valid_attrs.update(col.name for col in self.__class__.__table__.columns)
            
            invalid = [k for k in kwargs if k not in valid_attrs]
            if invalid:
                raise KeyError(
                    f"Invalid attribute(s) for {self.__class__.__name__} "
                    f"in DBStorage: {', '.join(invalid)}"
                )

    def save(self):
        """Updates timestamps and saves to storage"""
        self.updated_at = datetime.now()
        from models import storage
        storage.save()

    def to_dict(self):
        """Returns dictionary representation without SQLAlchemy state"""
        return {
            **{k: v.isoformat() if isinstance(v, datetime) else v 
               for k, v in self.__dict__.items() 
               if k != '_sa_instance_state'},
            '__class__': self.__class__.__name__
        }

    def delete(self):
        """Deletes instance from storage"""
        from models import storage
        storage.delete(self)

    def __str__(self):
        """String representation of the instance"""
        return f"[{self.__class__.__name__}] ({self.id}) {self.__dict__}"