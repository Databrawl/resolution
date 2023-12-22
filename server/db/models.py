from __future__ import annotations
from __future__ import annotations

import re
from contextvars import ContextVar
from typing import Any, List, Set, Dict, Callable
from uuid import uuid4

from llama_index.constants import DEFAULT_EMBEDDING_DIM
from pgvector.sqlalchemy import Vector
from sqlalchemy import String, UniqueConstraint, inspect as sa_inspect, UUID, ForeignKey
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import as_declarative, DeferredReflection
from sqlalchemy.orm import Mapped, declared_attr, InstanceState
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db import db


@as_declarative()
class _Base:
    """SQLAlchemy base class."""

    __abstract__ = True

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

    # noinspection PyMethodParameters
    @declared_attr
    def __tablename__(cls):
        """Convert class name to snake_case table name"""
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', cls.__name__).lower()

    @classmethod
    def get(cls, pk: str) -> Any:
        """Get an instance by primary key"""
        stmt = select(cls).where(cls.id == pk).limit(1)
        return db.session.execute(stmt).scalar_one()

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)


class BaseModel(_Base):
    """
    Separate BaseModel class to be able to include mixins and to Fix typing.

    This should be used instead of Base.
    """

    __abstract__ = True
    __table_args__ = {"schema": "public"}

    __init__: Callable[..., _Base]  # type: ignore

    def __repr__(self) -> str:
        inst_state: InstanceState = sa_inspect(self)
        attr_vals = [
            f"{attr.key}={getattr(self, attr.key)}"
            for attr in inst_state.mapper.column_attrs
            if attr.key not in ["tsv"]
        ]
        return f"{self.__class__.__name__}({', '.join(attr_vals)})"


class Reflected(DeferredReflection):
    __abstract__ = True


class ForeignKeyCascade(ForeignKey):
    def __init__(self, *args, **kwargs):
        kwargs['ondelete'] = "CASCADE"
        super().__init__(*args, **kwargs)


class User(BaseModel, Reflected):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}

    orgs = relationship("OrgUser", backref="user")


class Org(BaseModel):
    name: Mapped[str] = mapped_column(String(30))
    # relationships
    chunks = relationship("Chunk", backref="org")
    users = relationship("OrgUser", backref="org")

    # Not a column
    current: ContextVar[Org] = ContextVar('current')

    def similarity_search(self, embedding: list[float], k: int = 10) -> list[tuple[Chunk, float]]:
        """Search for similar chunks in this org"""
        q = select(Chunk, 1 - Chunk.embedding.cosine_distance(embedding)). \
            where(Chunk.org_id == self.id). \
            order_by(Chunk.embedding.cosine_distance(embedding)). \
            limit(k)
        return list(map(tuple, db.session.execute(q).all()))


class OrgUser(BaseModel):
    # Many-to-many between users and orgs, we need since we cannot modify Users table that is set by Supabase
    user_id: Mapped[str] = mapped_column(ForeignKeyCascade('auth.users.id'))
    org_id: Mapped[str] = mapped_column(ForeignKeyCascade(Org.id))


class Chunk(BaseModel):
    __table_args__ = (
        UniqueConstraint("org_id", "hash_value", name="org_hash_unique_together"),
    )

    org_id: Mapped[str] = mapped_column(ForeignKeyCascade(Org.id))

    data: Mapped[dict[str, Any]] = mapped_column(JSON)
    hash_value: Mapped[str] = mapped_column(String(64))
    embedding: Mapped[Vector] = mapped_column(Vector(DEFAULT_EMBEDDING_DIM))


Reflected.prepare(db.engine)
