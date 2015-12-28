from tests import BaseTestCase
from tests.factories import org_factory


class TestGroupDataSourceListResource(BaseTestCase):
    def test_returns_only_groups_for_current_org(self):
        group = self.factory.create_group(org=org_factory.create())
        data_source = self.factory.create_data_source(group=group)

        response = self.make_request('get', '/api/groups/{}/data_sources'.format(group.id), user=self.factory.create_admin())
        self.assertEqual(response.status_code, 404)



