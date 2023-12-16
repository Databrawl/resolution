from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from llama_index.constants import DEFAULT_EMBEDDING_DIM
from pgvector.sqlalchemy import Vector
from sqlalchemy import String, UniqueConstraint
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db import db
from db.database import BaseModel, ForeignKeyCascade, Reflected


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
    current: ContextVar[Mapped["Org"]] = ContextVar('current')

    def similarity_search(self, embedding: list[float], k: int = 10) -> list[tuple[Chunk, float]]:
        """Search for similar chunks in this org"""
        q = select(Chunk, 1 - Chunk.embedding.cosine_distance(embedding)). \
            where(Chunk.org_id == self.id). \
            order_by(Chunk.embedding.cosine_distance(embedding)). \
            limit(k)
        return list(map(tuple, db.session.get().execute(q).all()))


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
