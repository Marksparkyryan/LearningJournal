import datetime
from peewee import *

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin

DATABASE = SqliteDatabase("journal.db")


class User(UserMixin, Model):
    username = CharField(max_length=32, unique=True)
    email = CharField(max_length=64, unique=True)
    password = CharField()
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin
                )
        except IntegrityError:
            pass


class Entry(Model):
    author = ForeignKeyField(
        model=User,
        backref="entries",
        on_delete="CASCADE",
    )
    title = CharField(max_length=32, unique=True)
    content = TextField()
    date = DateField()
    time_spent = IntegerField()
    resources = TextField()
    slug = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_entry(cls, author, title, content, date, time_spent, resources):
        try:
            with DATABASE.transaction():
                # replace title whitespace with dashes
                joined = "-".join(title.lower().split())
                cls.create(
                    author=author,
                    title=title,
                    content=content,
                    date=date,
                    time_spent=time_spent,
                    resources=resources,
                    slug=joined,
                )
        except IntegrityError:
            pass

    def get_tags(self):
        """get users following current user"""
        return (
            Entry.select().join(
                EntryTag, on=EntryTag.entry
            ).where(
                EntryTag.tag == self
            )
        )


class Tag(Model):
    topic = CharField(max_length=12, unique=True)

    class Meta:
        database = DATABASE


class EntryTag(Model):
    entry = ForeignKeyField(model=Entry, backref="tags")
    tag = ForeignKeyField(model=Tag, backref="related_to")

    class Meta:
        database = DATABASE


def initialize_database():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry, Tag, EntryTag], safe=True)
    DATABASE.close()
