import datetime

import models


def dummy_data():
    """
    Populates database with dummy data for testing. Set DUMMYDATA to 
    False in app.py to prevent population.
    """

    try:
        models.User.create_user(
            username="JaneDoe",
            email="janedoe@email.com",
            password="password",
            admin=True
        )
        for i in range(1, 4):
            try:
                models.Entry.create_entry(
                    author=models.User.get_by_id(1),
                    title="Test Entry {}".format(i),
                    content="Lorem ipsum dolor sit amet, consectetur"
                             "adipiscing elit, sed do eiusmod tempor incididunt ut"
                             "labore et dolore magna aliqua. Ut enim ad minim veniam,"
                             "quis nostrud exercitation ullamco laboris nisi ut"
                             "aliquip ex ea commodo consequat. Duis aute irure dolor"
                             "in reprehenderit in voluptate velit esse cillum dolore"
                             "eu fugiat nulla pariatur. Excepteur sint occaecat"
                             "cupidatat non proident, sunt in culpa qui officia"
                             "deserunt mollit anim id est laborum.",
                    date=datetime.datetime.now(),
                    time_spent=i,
                )
                models.Tag.create(
                    topic="#tag{}".format(i),
                )
                models.EntryTag.create(
                    entry=models.Entry.get_by_id(i),
                    tag=models.Tag.get_by_id(i),
                )
                models.Resource.create(
                    entry=models.Entry.get_by_id(i),
                    title="Treehouse Lesson {} ".format(i),
                    link="https://www.teamtreehouse.com",
                )
            except models.IntegrityError:
                pass
    except ValueError:
        pass
