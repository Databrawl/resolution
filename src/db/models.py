import re
from uuid import uuid4

from llama_index.constants import DEFAULT_EMBEDDING_DIM
from pgvector.sqlalchemy import Vector
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
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


class User(Base, Reflected):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}


class Org(Base):
    name: Mapped[str] = mapped_column(String(30))
    # relationships
    chunks = relationship("Chunk", backref="org")


class OrgUser(Base):
    # Many-to-many between users and orgs, we need since we cannot modify Users table that is set by Supabase
    user_id = mapped_column(ForeignKey('auth.users.id'))
    org_id: Mapped[int] = mapped_column(ForeignKey(Org.id))


class Chunk(Base):
    org_id: Mapped[int] = mapped_column(ForeignKey(Org.id))

    embedding = mapped_column(Vector(DEFAULT_EMBEDDING_DIM))
