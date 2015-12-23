from flask import request
from flask.ext.restful import abort
from redash import models
from redash.wsgi import api
from redash.tasks import record_event
from redash.permissions import require_permission, require_admin_or_owner, is_admin_or_owner, \
    require_permission_or_owner
from redash.handlers.base import BaseResource, require_fields, get_object_or_404


class GroupListResource(BaseResource):
    def get(self):
        if self.current_user.has_permission('admin'):
            groups = models.Group.all(self.current_org)
        else:
            groups = models.Group.select().where(models.Group.id << self.current_user.groups)

        return [g.to_dict() for g in groups]


class GroupResource(BaseResource):
    def get(self, group_id):
        if not (self.current_user.has_permission('admin') or int(group_id) in self.current_user.groups):
            abort(403)

        group = models.Group.get_by_id_and_org(group_id, self.current_org)

        return group.to_dict()


class GroupMemberListResource(BaseResource):
    @require_permission('admin')
    def post(self, group_id):
        user_id = request.json['user_id']
        user = models.User.get_by_id_and_org(user_id, self.current_org)
        group = models.Group.get_by_id_and_org(group_id, self.current_org)
        user.groups.append(group.id)
        user.save()

        return user.to_dict()

    def get(self, group_id):
        if not (self.current_user.has_permission('admin') or int(group_id) in self.current_user.groups):
            abort(403)

        members = models.Group.members(group_id)
        return [m.to_dict() for m in members]


class GroupMemberResource(BaseResource):
    @require_permission('admin')
    def delete(self, group_id, user_id):
        user = models.User.get_by_id_and_org(user_id, self.current_org)
        user.groups.remove(int(group_id))
        user.save()


class GroupDataSourceListResource(BaseResource):
    @require_permission('admin')
    def post(self, group_id):
        data_source_id = request.json['data_source_id']
        data_source = models.DataSource.get_by_id_and_org(data_source_id, self.current_org)
        group = models.Group.get_by_id_and_org(group_id, self.current_org)

        data_source.add_group(group)

        return data_source.to_dict(with_permissions=True)

    @require_permission('admin')
    def get(self, group_id):
        # TODO: check group is in current org
        # TOOD: move to models
        data_sources = models.DataSource.select(models.DataSource, models.DataSourceGroup.view_only)\
            .join(models.DataSourceGroup)\
            .where(models.DataSourceGroup.group == group_id)

        return [ds.to_dict(with_permissions=True) for ds in data_sources]


class GroupDataSourceResource(BaseResource):
    @require_permission('admin')
    def post(self, group_id, data_source_id):
        data_source = models.DataSource.get_by_id_and_org(data_source_id, self.current_org)
        group = models.Group.get_by_id_and_org(group_id, self.current_org)
        view_only = request.json['view_only']

        data_source.update_group_permission(group, view_only)

        return data_source.to_dict(with_permissions=True)

    @require_permission('admin')
    def delete(self, group_id, data_source_id):
        data_source = models.DataSource.get_by_id_and_org(data_source_id, self.current_org)
        group = models.Group.get_by_id_and_org(group_id, self.current_org)

        data_source.remove_group(group)


api.add_resource(GroupListResource, '/api/groups', endpoint='groups')
api.add_resource(GroupResource, '/api/groups/<group_id>', endpoint='group')
api.add_resource(GroupMemberListResource, '/api/groups/<group_id>/members', endpoint='group_members')
api.add_resource(GroupMemberResource, '/api/groups/<group_id>/members/<user_id>', endpoint='group_member')
api.add_resource(GroupDataSourceListResource, '/api/groups/<group_id>/data_sources', endpoint='group_data_sources')
api.add_resource(GroupDataSourceResource, '/api/groups/<group_id>/data_sources/<data_source_id>', endpoint='group_data_source')
