from ..models import User
from ..models.user import UserAccess


def get_user(id: int):
    user = User.get_or_none(id=id)

    return user


def get_user_accesses(id: int):
    accesses = UserAccess.select().where(UserAccess.user == id)
    return list(accesses)


def create_user(id: int, name: str, username: str):
    user = User.create(id=id, name=name, username=username)

    return user


def get_or_create_user(id: int, name: str, username: str):
    user = get_user(id)
    if user:
        user.name = name
        user.username = username
        user.save()
    else:
        user = create_user(id, name, username)

    return user
