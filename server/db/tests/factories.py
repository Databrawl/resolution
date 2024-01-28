import random
from hashlib import sha256

import factory
from factory import lazy_attribute
from llama_index.constants import DEFAULT_EMBEDDING_DIM

from db import db
from db.models import User, Org, Chunk, OrgUser


class Options(factory.alchemy.SQLAlchemyOptions):
    class Meta:
        abstract = True

    @staticmethod
    def _check_has_sqlalchemy_session_set(meta, value):
        try:
            if value and meta.sqlalchemy_session:
                raise RuntimeError("Provide either a sqlalchemy_session or a sqlalchemy_session_"
                                   "factory, not both")
        except AttributeError:
            pass


class ModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    _options_class = Options

    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'


class UserFactory(ModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")


class OrgFactory(ModelFactory):
    class Meta:
        model = Org

    name = factory.Faker("company")


class OrgUserFactory(ModelFactory):
    class Meta:
        model = OrgUser

    org = factory.SubFactory(OrgFactory)
    user = factory.SubFactory(UserFactory)


class ChunkFactory(ModelFactory):
    class Meta:
        model = Chunk

    org = factory.SubFactory(OrgFactory)
    data = factory.Dict(
        {
            "text": factory.Faker("text"),
            "metadata": factory.Dict(
                {
                    "key": factory.Faker("name")
                }
            )
        }
    )

    @lazy_attribute
    def hash_value(self):
        return sha256(self.data["text"].encode()).hexdigest()

    @lazy_attribute
    def embedding(self):
        return [round(random.random(), 2) for _ in range(DEFAULT_EMBEDDING_DIM)]
