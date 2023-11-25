import re
from typing import Any
from uuid import uuid4

from llama_index.constants import DEFAULT_EMBEDDING_DIM
from pgvector.sqlalchemy import Vector
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import DeclarativeBase, declared_attr, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    """subclasses will be converted to dataclasses"""
    __abstract__ = True

    # noinspection PyMethodParameters
    @declared_attr
    def __tablename__(cls):
        """Convert class name to snake_case table name"""
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', cls.__name__).lower()

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)


class Reflected(DeferredReflection):
    __abstract__ = True


class ForeignKeyCascade(ForeignKey):
    def __init__(self, *args, **kwargs):
        kwargs['ondelete'] = "CASCADE"
        super().__init__(*args, **kwargs)


class User(Base, Reflected):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}


class Org(Base):
    name: Mapped[str] = mapped_column(String(30))
    # relationships
    chunks = relationship("Chunk", backref="org")

    # TODO: use centralized session
    def similarity_search(self, session, embedding: list[float], k: int = 10):
        """Search for similar chunks in this org"""
        q = select(Chunk). \
            where(Chunk.org_id == self.id). \
            order_by(Chunk.embedding.cosine_distance(embedding)). \
            limit(k)
        print(q)
        res = session.execute(q)
        return list(map(lambda r: r.Chunk, res))


class OrgUser(Base):
    # Many-to-many between users and orgs, we need since we cannot modify Users table that is set by Supabase
    user_id = mapped_column(ForeignKeyCascade('auth.users.id'))
    org_id: Mapped[int] = mapped_column(ForeignKeyCascade(Org.id))


class Chunk(Base):
    __table_args__ = (
        UniqueConstraint("org_id", "embedding", name="org_embedding_unique_together"),
    )

    org_id: Mapped[int] = mapped_column(ForeignKeyCascade(Org.id))

    text: Mapped[str] = mapped_column(String)
    embedding: Mapped[Vector] = mapped_column(Vector(DEFAULT_EMBEDDING_DIM))
    meta_data: Mapped[dict[str, Any]] = mapped_column(JSON)
