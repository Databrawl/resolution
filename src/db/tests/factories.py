import factory

from db import db_session
from db.models import User, Org


class Options(factory.alchemy.SQLAlchemyOptions):
    class Meta:
        abstract = True

    @staticmethod
    def _check_has_sqlalchemy_session_set(meta, value):
        try:
            if value and meta.sqlalchemy_session:
                raise RuntimeError("Provide either a sqlalchemy_session or a sqlalchemy_session_factory, not both")
        except AttributeError:
            pass


class ModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    _options_class = Options

    class Meta:
        abstract = True
        sqlalchemy_session_factory = db_session.get
        sqlalchemy_session = None
        sqlalchemy_session_persistence = 'commit'


class UserFactory(ModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")


class OrgFactory(ModelFactory):
    class Meta:
        model = Org

    name = factory.Faker("company")
