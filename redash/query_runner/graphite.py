import json
import datetime
import requests
import logging
from redash.query_runner import *
from redash.utils import JSONEncoder

logger = logging.getLogger(__name__)


def _transform_result(response):
    columns = ({'name': 'Time::x', 'type': TYPE_DATETIME},
               {'name': 'value::y', 'type': TYPE_FLOAT},
               {'name': 'name::series', 'type': TYPE_STRING})

    rows = []

    for series in response.json():
        for values in series['datapoints']:
            timestamp = datetime.datetime.fromtimestamp(int(values[1]))
            rows.append({'Time::x': timestamp, 'name::series': series['target'], 'value::y': values[0]})

    data = {'columns': columns, 'rows': rows}
    return json.dumps(data, cls=JSONEncoder)


class Graphite(BaseQueryRunner):
    @classmethod
    def configuration_schema(cls):
        return {
            'type': 'object',
            'properties': {
                'url': {
                    'type': 'string'
                },
                'username': {
                    'type': 'string'
                },
                'password': {
                    'type': 'string'
                },
                'verify': {
                    'type': 'boolean',
                    'title': 'Verify SSL certificate'
                }
            },
            'required': ['url'],
            'secret': ['password']
        }

    @classmethod
    def annotate_query(cls):
        return False

    def __init__(self, configuration_json):
        super(Graphite, self).__init__(configuration_json)

        if "username" in self.configuration and self.configuration["username"]:
            self.auth = (self.configuration["username"], self.configuration["password"])
        else:
            self.auth = None

        self.verify = self.configuration.get("verify", True)
        self.base_url = "%s/render?format=json&" % self.configuration['url']

    def run_query(self, query):
        url = "%s%s" % (self.base_url, "&".join(query.split("\n")))
        error = None
        data = None

        try:
            response = requests.get(url, auth=self.auth, verify=self.verify)

            if response.status_code == 200:
                data = _transform_result(response)
            else:
                error = "Failed getting results (%d)" % response.status_code
        except Exception, ex:
            data = None
            error = ex.message

        return data, error

register(Graphite)
