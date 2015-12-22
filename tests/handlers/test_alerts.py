from tests import BaseTestCase
from tests.handlers import authenticated_user, json_request
from redash.wsgi import app


class TestAlertResourceGet(BaseTestCase):
    def test_returns_200_if_allowed(self):
        alert = self.factory.create_alert()

        with app.test_client() as c, authenticated_user(c, user=self.factory.user):
            rv = json_request(c.get, "/api/alerts/{}".format(alert.id))
            self.assertEqual(rv.status_code, 200)

    def test_returns_403_if_not_allowed(self):
        data_source = self.factory.create_data_source(group=self.factory.create_group())
        query = self.factory.create_query(data_source=data_source)
        alert = self.factory.create_alert(query=query)

        with app.test_client() as c, authenticated_user(c, user=self.factory.user):
            rv = json_request(c.get, "/api/alerts/{}".format(alert.id))
            self.assertEqual(rv.status_code, 403)


class TestAlertListPost(BaseTestCase):
    def test_returns_200_if_has_access_to_query(self):
        query = self.factory.create_query()

        with app.test_client() as c, authenticated_user(c, user=self.factory.user):
            rv = json_request(c.post, "/api/alerts", data=dict(name='Alert', query_id=query.id, options={}))
            self.assertEqual(rv.status_code, 200)

    def test_fails_if_doesnt_have_access_to_query(self):
        data_source = self.factory.create_data_source(group=self.factory.create_group())
        query = self.factory.create_query(data_source=data_source)

        with app.test_client() as c, authenticated_user(c, user=self.factory.user):
            rv = json_request(c.post, "/api/alerts", data=dict(name='Alert', query_id=query.id, options={}))
            self.assertEqual(rv.status_code, 403)


class TestAlertSubscriptionListResourcePost(BaseTestCase):
    def test_subscribers_user_to_alert(self):
        alert = self.factory.create_alert()

        with app.test_client() as c, authenticated_user(c, user=self.factory.user):
            rv = json_request(c.post, "/api/alerts/{}/subscriptions".format(alert.id))
            self.assertEqual(rv.status_code, 200)
            self.assertIn(self.factory.user, alert.subscribers())

    def test_doesnt_subscribers_user_to_alert_without_access(self):
        data_source = self.factory.create_data_source(group=self.factory.create_group())
        query = self.factory.create_query(data_source=data_source)
        alert = self.factory.create_alert(query=query)

        with app.test_client() as c, authenticated_user(c, user=self.factory.user):
            rv = json_request(c.post, "/api/alerts/{}/subscriptions".format(alert.id))
            self.assertEqual(rv.status_code, 403)
            self.assertNotIn(self.factory.user, alert.subscribers())


class TestAlertSubscriptionListResourceGet(BaseTestCase):
    def test_returns_subscribers(self):
        alert = self.factory.create_alert()

        with app.test_client() as c, authenticated_user(c, user=self.factory.user):
            rv = json_request(c.get, "/api/alerts/{}/subscriptions".format(alert.id))
            self.assertEqual(rv.status_code, 200)

    def test_doesnt_return_subscribers_when_not_allowed(self):
        data_source = self.factory.create_data_source(group=self.factory.create_group())
        query = self.factory.create_query(data_source=data_source)
        alert = self.factory.create_alert(query=query)

        with app.test_client() as c, authenticated_user(c, user=self.factory.user):
            rv = json_request(c.get, "/api/alerts/{}/subscriptions".format(alert.id))
            self.assertEqual(rv.status_code, 403)
