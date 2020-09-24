# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: September 4th 2020

Modified By: hsky77
Last Updated: September 17th 2020 15:53:39 pm
'''

import json
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Tuple, List, Union

from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from hyssop.util import BaseLocal

from .utils import str_to_datetime
from .constants import LocalCode_Invalid_Column


DeclarativeBases: dict = {}


def get_declarative_base(key: str = 'default') -> DeclarativeMeta:
    """
    get entity class declarative meta class
    """
    if not key in DeclarativeBases:
        DeclarativeBases[key] = declarative_base()
    return DeclarativeBases[key]


Entity = DeclarativeMeta


class EntityMixin():
    """
    This is helper functions for sqlalchemy entity
    """

    @classmethod
    def columns(cls) -> List[str]:
        """
        Get list of column names
        """
        return [x.name for x in inspect(cls).columns]

    @classmethod
    def primary_keys(cls) -> List[str]:
        """
        Get list of primary key column names
        """
        return [x.name for x in inspect(cls).primary_key]

    @classmethod
    def non_primary_keys(cls) -> List[str]:
        """
        Get list of non-primary key column names
        """
        pkeys = cls.primary_keys()
        return [x for x in cls.columns() if not x in pkeys]

    @property
    def identity(self) -> Tuple[Any]:
        """
        Get identity of this entity, this is a tuple of primary key columns' value
        """
        return self._sa_instance_state.identity

    @property
    def key_values(self) -> Dict[str, Any]:
        """
        Get dict contains columns
        """
        return {k: getattr(self, k) for k in self.columns()}

    @property
    def primary_key_values(self) -> Dict[str, Any]:
        """
        Get dict contains primary key columns
        """
        return {k: getattr(self, k) for k in self.primary_keys()}

    @property
    def non_primary_key_values(self) -> Dict[str, Any]:
        """
        Get dict contains non-primary key columns
        """
        return {k: getattr(self, k) for k in self.non_primary_keys()}

    def equals(self, right: Entity) -> bool:
        """
        Compare two entities
        """
        if issubclass(type(right), EntityMixin):
            r = right.key_values
            l = self.key_values
            for k, v in r.items():
                if not l[k] == v:
                    return False
            return True
        return False

    def to_json_dict(self) -> Dict[str, Any]:
        """
        Generate dict that is serializable by Json convertor
        """
        return {k: v if not type(v) is datetime else str(v) for k, v in self.key_values.items()}


Entity = Union[DeclarativeMeta, EntityMixin]


class IUnitOfWork():
    """
    This inteface defines the basic methods to access the orm entities.

    Note: orm session instance is required as the first argument when defining or overriding functions.
    """

    def select(self, session: Session, **kwargs) -> List[Entity]:
        """
        Select database with or without keys and return a list of entities.
        """
        raise NotImplementedError()

    def load(self, session: Session, **kwargs) -> Entity:
        """
        Select database with or without keys, and return first matched entity.
        """
        raise NotImplementedError()

    def delete(self, session: Session, entities: List[Entity], **kwargs) -> None:
        """
        Delete a list of entities from database.
        """
        raise NotImplementedError()

    def add(self, session: Session, **kwargs) -> Entity:
        """
        Insert one entity. Raise exception if it exists.
        """
        raise NotImplementedError()

    def merge(self, session: Session, **kwargs) -> Entity:
        """
        Insert or replace one entity.
        """
        raise NotImplementedError()

    def update(self, session: Session, entity: Entity, **kwargs) -> None:
        """
        Update entity values.
        """
        raise NotImplementedError()

    def relationship_merge(self, session: Session, parent: Entity, name: str, child: Entity):
        """
        append entity to relationship field
        """
        raise NotImplementedError()

    def relationship_remove(self, session: Session, parent: Entity, name: str, child: Entity):
        """
        remove entity from relationship field
        """
        raise NotImplementedError()

    def validate(self, entity: Entity, raise_exception: bool = True) -> bool:
        """
        Validate entity column values.
        """
        raise NotImplementedError()

    def refresh(self, session: Session, entity: Entity) -> Entity:
        """
        Refresh entity from database.
        """
        raise NotImplementedError()

    def flush(self, session: Session) -> Tuple[int, int, int]:
        """
        Flush the session of database connection. Return changes (new, updated, deleted)
        """
        raise NotImplementedError()

    def rollback(self, session: Session) -> None:
        """
        Rollback the session of database connection.
        """
        raise NotImplementedError()

    def commit(self, session: Session) -> Tuple[int, int, int]:
        """
        Commit the changes to the database. Return changes (new, updated, deleted)
        """
        raise NotImplementedError()


class BasicUW(IUnitOfWork):
    def __init__(self, entity_cls: Entity = None):
        super().__init__()
        if entity_cls is not None:
            self.set_entity_cls(entity_cls)

    def set_entity_cls(self, entity_cls: Entity) -> None:
        self.entity_cls = entity_cls

    def select(self, session: Session, **kwargs) -> List[Entity]:
        """
        Select database with or without keys and return a list of entities
        """
        if len(kwargs) > 0:
            qobj = session.query(self.entity_cls).filter_by(**kwargs)
        else:
            qobj = session.query(self.entity_cls)

        return [o for o in qobj]

    def load(self, session: Session, **kwargs) -> Entity:
        """
        Select database with or without keys, and return first matched entity
        """
        if len(kwargs) > 0:
            return session.query(self.entity_cls).filter_by(**kwargs).first()

    def delete(self, session: Session, entities: List[Entity], **kwargs) -> None:
        """
        Delete a list of entities from database
        """
        if not isinstance(entities, list):
            entities = [entities]

        for entity in entities:
            session.delete(entity)

    def add(self, session: Session, **kwargs) -> Entity:
        """
        Insert one entity. Raise exception if it exists.
        """
        entity = self.entity_cls()
        session.add(entity)
        self.update(session, entity, **kwargs)
        return entity

    def merge(self, session: Session, **kwargs) -> Entity:
        """
        Insert or replace one entity.
        """
        entity = self.load(session, **kwargs)
        if entity is None:
            entity = self.add(session, **kwargs)
        else:
            self.update(
                session, entity,
                **{k: v for k, v in kwargs.items() if k in self.entity_cls.non_primary_keys()})
        return entity

    def update(self, session: Session, entity: Entity, **kwargs) -> None:
        """
        Update entity values
        """
        for k, v in kwargs.items():
            if hasattr(entity, k):
                if isinstance(getattr(entity, k), datetime):
                    if isinstance(v, str):
                        setattr(entity, k, str_to_datetime(v))
                    else:
                        setattr(entity, k, v)
                else:
                    setattr(entity, k, v)
            else:
                raise RuntimeError(LocalCode_Invalid_Column, k)

    def relationship_merge(self, session: Session, parent: Entity, name: str, child: Entity):
        """
        append entity to relationship field
        """
        f = getattr(parent, name)
        if not child in f:
            f.append(child)

    def relationship_remove(self, session: Session, parent: Entity, name: str, child: Entity):
        """
        remove entity from relationship field
        """
        f = getattr(parent, name)
        if child in f:
            f.remove(child)

    def refresh(self, session: Session, entity: Entity) -> Entity:
        """
        Refresh entity from database
        """
        session.refresh(entity)
        return entity

    def flush(self, session: Session) -> Tuple[int, int, int]:
        """
        Flush the session of database connection. Return changes (new, updated, deleted)
        """
        try:
            changed = (len(session.new), len(
                session.dirty), len(session.deleted))
            session.flush()
            return changed
        except:
            self.rollback(session)
            raise

    def rollback(self, session: Session) -> None:
        """
        Rollback the session of database connection
        """
        session.rollback()

    def commit(self, session: Session) -> Tuple[int, int, int]:
        """
        Commit the changes to the database. Return changes (new, updated, deleted)
        """
        try:
            changed = (len(session.new), len(
                session.dirty), len(session.deleted))
            session.commit()
            return changed
        except:
            self.rollback(session)
            raise
