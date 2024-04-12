from __future__ import annotations
from __future__ import annotations

from contextvars import ContextVar
from datetime import datetime
from typing import Any

from llama_index.core.constants import DEFAULT_EMBEDDING_DIM
from pgvector.sqlalchemy import Vector
from sqlalchemy import String, UniqueConstraint, Boolean, \
    DateTime, Text
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from db import db, ForeignKeyCascade


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    org_users = relationship("OrgUser", backref="user")
    chats = relationship("Chat", backref="user")

    current: ContextVar[Org] = ContextVar('current_user')


class Org(db.Model):
    name: Mapped[str] = mapped_column(String(30))
    # relationships
    chunks = relationship("Chunk", backref="org")
    org_users = relationship("OrgUser", backref="org")

    # Not a column
    current: ContextVar[Org] = ContextVar('current_org')

    def similarity_search(self, embedding: list[float], k: int = 10) -> list[tuple[Chunk, float]]:
        """Search for similar chunks in this org"""
        q = select(Chunk, 1 - Chunk.embedding.cosine_distance(embedding)). \
            where(Chunk.org_id == self.id). \
            order_by(Chunk.embedding.cosine_distance(embedding)). \
            limit(k)
        return list(map(tuple, db.session.execute(q).all()))


class OrgUser(db.Model):
    # Many-to-many between users and orgs, we need since we cannot modify Users table that is set by Supabase
    user_id: Mapped[str] = mapped_column(ForeignKeyCascade('auth.users.id'))
    org_id: Mapped[str] = mapped_column(ForeignKeyCascade(Org.id))


class Chunk(db.Model):
    __table_args__ = (
        UniqueConstraint("org_id", "hash_value", name="org_hash_unique_together"),
    )

    org_id: Mapped[str] = mapped_column(ForeignKeyCascade(Org.id))

    data: Mapped[dict[str, Any]] = mapped_column(JSON)
    hash_value: Mapped[str] = mapped_column(String(64))
    embedding: Mapped[Vector] = mapped_column(Vector(DEFAULT_EMBEDDING_DIM))


class Chat(db.Model):
    name: Mapped[str] = mapped_column(String(1024))
    user_id: Mapped[str] = mapped_column(ForeignKeyCascade(User.id))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    messages = relationship("Message", backref="chat")


class Message(db.Model):
    chat_id: Mapped[str] = mapped_column(ForeignKeyCascade(Chat.id))
    user_message: Mapped[str] = mapped_column(String(1024), nullable=False)
    ai_message: Mapped[str] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class Onboarding(db.Model):
    org_id: Mapped[str] = mapped_column(ForeignKeyCascade(Org.id))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    greeting: Mapped[str] = mapped_column(Text, nullable=False)
    quick_1: Mapped[str] = mapped_column(Text)
    quick_2: Mapped[str] = mapped_column(Text)
    quick_3: Mapped[str] = mapped_column(Text)
