import functools
from flask.ext.login import current_user
from flask.ext.restful import abort
from funcy import distinct, flatten


def assert_access(object_groups, user, required_permission):
    if 'admin' in user.permissions:
        # TODO: remove duplication
        return 'view', 'create'

    matching_groups = set(object_groups.keys()).intersection(user.groups)

    if not matching_groups:
        abort(403)

    permissions = distinct(flatten([object_groups[group] for group in matching_groups]))
    if required_permission not in permissions:
        abort(403)

    return permissions


class require_permissions(object):
    def __init__(self, permissions):
        self.permissions = permissions

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            has_permissions = current_user.has_permissions(self.permissions)

            if has_permissions:
                return fn(*args, **kwargs)
            else:
                abort(403)

        return decorated


def require_permission(permission):
    return require_permissions((permission,))


def has_permission_or_owner(permission, object_owner_id):
    return int(object_owner_id) == current_user.id or current_user.has_permission(permission)


def is_admin_or_owner(object_owner_id):
    return has_permission_or_owner('admin', object_owner_id)


def require_permission_or_owner(permission, object_owner_id):
    if not has_permission_or_owner(permission, object_owner_id):
        abort(403)


def require_admin_or_owner(object_owner_id):
    if not is_admin_or_owner(object_owner_id):
        abort(403, message="You don't have permission to edit this resource.")
