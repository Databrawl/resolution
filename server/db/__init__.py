# from db.database import Database
# from settings import app_settings
#
# db = Database(app_settings.SQLALCHEMY_DATABASE_URI)


from __future__ import annotations

import re
from typing import List, Set, Dict, Any
from uuid import uuid4
from utils.json import json_dumps, json_loads

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect as sa_inspect, select, UUID, ForeignKey
from sqlalchemy.orm import DeclarativeBase, declared_attr, InstanceState, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    """
    Separate BaseModel class to be able to include mixins and to Fix typing.

    This should be used instead of Base.
    """

    __abstract__ = True
    __table_args__ = {"schema": "public"}

    _json_include: List = []
    _json_exclude: List = []

    def __json__(self, excluded_keys: Set = None) -> Dict:  # noqa: B006
        if excluded_keys is None:
            excluded_keys = set()
        ins = sa_inspect(self)

        columns = set(ins.mapper.column_attrs.keys())
        relationships = set(ins.mapper.relationships.keys())
        unloaded = ins.unloaded
        expired = ins.expired_attributes
        include = set(self._json_include)
        exclude = set(self._json_exclude) | set(excluded_keys)

        # This set of keys determines which fields will be present in
        # the resulting JSON object.
        # Here we initialize it with properties defined by the model class,
        # and then add/delete some columns below in a tricky way.
        keys = columns | relationships

        # 1. Remove not yet loaded properties.
        # Basically this is needed to serialize only .join()'ed relationships
        # and omit all other lazy-loaded things.
        if not ins.transient:
            # If the entity is not transient -- exclude unloaded keys
            # Transient entities won't load these anyway, so it's safe to
            # include all columns and get defaults
            keys -= unloaded

        # 2. Re-load expired attributes.
        # At the previous step (1) we substracted unloaded keys, and usually
        # that includes all expired keys. Actually we don't want to remove the
        # expired keys, we want to refresh them, so here we have to re-add them
        # back. And they will be refreshed later, upon first read.
        if ins.expired:
            keys |= expired

        # 3. Add keys explicitly specified in _json_include list.
        # That allows you to override those attributes unloaded above.
        # For example, you may include some lazy-loaded relationship() there
        # (which is usually removed at the step 1).
        keys |= include

        # 4. For objects in `deleted` or `detached` state, remove all
        # relationships and lazy-loaded attributes, because they require
        # refreshing data from the DB, but this cannot be done in these states.
        # That is:
        #  - if the object is deleted, you can't refresh data from the DB
        #    because there is no data in the DB, everything is deleted
        #  - if the object is detached, then there is no DB session associated
        #    with the object, so you don't have a DB connection to send a query
        # So in both cases you get an error if you try to read such attributes.
        if ins.deleted or ins.detached:
            keys -= relationships
            keys -= unloaded

        # 5. Delete all explicitly black-listed keys.
        # That should be done last, since that may be used to hide some
        # sensitive data from JSON representation.
        keys -= exclude

        return {key: getattr(self, key) for key in keys}

    @declared_attr
    def __tablename__(cls):
        """Convert class name to snake_case table name"""
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', cls.__name__).lower()

    @classmethod
    def get(cls, pk: str) -> Any:
        """Get an instance by primary key"""
        stmt = select(cls).where(cls.id == pk).limit(1)
        return db.session.execute(stmt).scalar_one()

    def __repr__(self) -> str:
        inst_state: InstanceState = sa_inspect(self)
        attr_vals = [
            f"{attr.key}={getattr(self, attr.key)}"
            for attr in inst_state.mapper.column_attrs
            if attr.key not in ["tsv"]
        ]
        return f"{self.__class__.__name__}({', '.join(attr_vals)})"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)


class ForeignKeyCascade(ForeignKey):
    def __init__(self, *args, **kwargs):
        kwargs['ondelete'] = "CASCADE"
        super().__init__(*args, **kwargs)


ENGINE_ARGUMENTS = {
    "connect_args": {"connect_timeout": 10, "options": "-c timezone=UTC"},
    "pool_pre_ping": True,
    "pool_size": 60,
    "json_serializer": json_dumps,
    "json_deserializer": json_loads,
}
SESSION_ARGUMENTS = {
    "expire_on_commit": False,  # this is needed, so we can use ORM objects after session is closed
}


db = SQLAlchemy(model_class=BaseModel, engine_options=ENGINE_ARGUMENTS, session_options=SESSION_ARGUMENTS)
