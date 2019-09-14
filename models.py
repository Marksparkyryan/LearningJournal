from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import (Model, CharField, BooleanField, IntegerField, TextField,
                    ForeignKeyField, DateField, IntegrityError, SqliteDatabase,
                    DoesNotExist)


DATABASE = SqliteDatabase("journal.db", pragmas={'foreign_keys': 1})


class User(UserMixin, Model):
    """User that can create, edit, and delete Entries

    Attributes:
    username (str): user's name that will be displayed within app
    email (str): user's email address
    password (str): user's password (hashed)
    is_admin (bool): user's admin status 

    Methods:
    create_user : instantiates User

    Returns:
    Instance of User
    """

    username = CharField(max_length=32, unique=True)
    email = CharField(max_length=64, unique=True)
    password = CharField()
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        """Instantiates User

        Parameters:
        @param username (str): user's name that will be displayed within app
        email (str): user's email address
        password (str): this gets hashed
        is_admin (bool): by default is False, make True if user is admin

        Returns:
        Instance of User
        """

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
    """Journal entry of a learning moment

    Attributes:
    author (foreign key): author of Entry
    title (str): title of Entry
    content (str): content of Entry
    date (datetime): date of Entry
    time_spent (int): amount of time spent on learning content
    slug (str): url-friendly version of entry title

    Methods:
    create_entry : instantiates entry
    tags : returns all tags related to entry in string format
    resources : returns all resources related to entry in string format

    Returns:
    Instance of Entry
    """

    author = ForeignKeyField(
        model=User,
        backref="entries",
        on_delete="CASCADE",
    )
    title = CharField(max_length=32, unique=True)
    content = TextField()
    date = DateField()
    time_spent = IntegerField()
    slug = CharField(unique=True)

    class Meta:
        database = DATABASE

    @classmethod
    def create_entry(cls, author, title, content, date, time_spent):
        """Instantiates Entry

        Parameters:
        author (foreign key): author of Entry
        title (str): title of Entry
        content (str): content of Entry
        date (datetime): date of Entry
        time_spent (int): amount of time spent on learning content
        slug (str): url-friendly version of entry title

        Returns:
        Instance of Entry
        """

        try:
            with DATABASE.transaction():
                cls.create(
                    author=author,
                    title=title,
                    content=content,
                    date=date,
                    time_spent=time_spent,
                    slug="-".join(title.lower().split()),
                )
        except IntegrityError:
            return IntegrityError

    @property
    def tags(self):
        """Hashtags related to an Entry instance

        Attributes:
        topic (str): topic of the tag

        Returns:
        Space separated string format of all tags related to instance of 
        Entry
        """

        query = Tag.select().join(
            EntryTag, on=EntryTag.tag
        ).where(
            EntryTag.entry == self
        )
        tag_text = ""
        for tag in query:
            tag_text += tag.topic + " "
        return tag_text

    @property
    def resources(self):
        """Resources related to an Entry instance

        Attributes:
        title (str): title of the Resource
        link (str): full hyperlink of resource

        Returns:
        Space separated string of Resource title and link. Each
        Resource is placed on a new line.  
        """

        query = Resource.select().where(
            Resource.entry == self
        )
        resource_text = ""
        for resource in query:
            if resource.link:
                resource_text += resource.title + resource.link + "\n"
            else:
                resource_text += resource.title + "\n"
        return resource_text


class Resource(Model):
    """Record of sources of knowledge

    Parameters:
    entry (foreign key): entry that Resource is related to
    title (str): title of Resource
    link (str): full hyperlink of Resource (optional)

    Returns:
    Instance of Resource
    """

    entry = ForeignKeyField(
        model=Entry, backref="rez", on_delete="CASCADE"
    )
    title = CharField()
    link = CharField(null=True)

    class Meta:
        database = DATABASE


class Tag(Model):
    """Hashtag that can be used to filter Entry by topic

    Parameters:
    topic (str): topic of the tag

    Returns:
    Instance of Tag
    """

    topic = CharField(max_length=12, unique=True)

    class Meta:
        database = DATABASE


class EntryTag(Model):
    """Creates relationship betweeen each Tag and each Entry

    Parameters:
    entry (foreign key): Entry model related to Tag
    tag (foreign key): Tag model related to Entry

    Returns:
    Instance of EntryTag relationship
    """

    entry = ForeignKeyField(model=Entry, backref="tagz", on_delete="CASCADE")
    tag = ForeignKeyField(model=Tag, backref="related_to")

    class Meta:
        database = DATABASE
        indexes = (
            (("entry", "tag"), True),
        )


def initialize_database():
    """Build database and database tables"""

    DATABASE.connect()
    DATABASE.create_tables([User, Entry, Resource, Tag, EntryTag], safe=True)
    DATABASE.close()
