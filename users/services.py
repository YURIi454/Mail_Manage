MANAGER_GROUP_NAME = "moderators"


def is_manager(user):
    """ Является ли пользователь менеджером (модератором) сервиса. """

    if not getattr(user, "is_authenticated", False):
        return False

    if user.is_superuser:
        return True

    return user.groups.filter(name=MANAGER_GROUP_NAME).exists()
