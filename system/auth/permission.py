from apps.user.models import UserTypes


def get_permitted_url_list_by_user_type(id=None):
    user_type_permission = UserTypes.objects.get(id=id).permission
    permission_list = []
    if len(user_type_permission) > 0:
        for key, value in user_type_permission.items():
            if len(value) > 0:
                for k in value:
                    permission_list.append(k)

    return permission_list
