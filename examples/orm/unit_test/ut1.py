import os
import json
from datetime import datetime, timedelta

from hyssop.util import join_path
from hyssop.unit_test import UnitTestCase, UnitTestServer
from hyssop.web.config_validator import WebConfigRootValidator
from hyssop.web.component import get_default_component_manager, DefaultComponentTypes
from hyssop.web.component.default import ServicesComponent


class UT1TestCase(UnitTestCase):
    def test(self):
        # implement unit test here...
        root_dir = os.path.dirname(os.path.dirname(__file__))

        with open(join_path(root_dir, 'server_config.yaml'), 'r') as f:
            import yaml
            validator = WebConfigRootValidator(
                yaml.load(f, Loader=yaml.SafeLoader))
            settings = validator.parameter

        server = UnitTestServer(debug=True)
        server.set_config(
            root_dir, settings['component'], settings['controller'])
        server.start()

        component_manager = get_default_component_manager(root_dir)

        service: ServicesComponent = component_manager.get_component(
            DefaultComponentTypes.Service)

        api = 'http://localhost:58564/testEntity'

        try:
            response = service.invoke(api)
            self.assertEqual(response.status_code, 200)
            res = json.loads(response.text)
            self.assertEqual(len(res['test_entities']), 0)

            response = service.invoke(api, 'put', data={
                'name': 'test',
                'age': 25,
                'gender': 'male',
                'schedule': str(datetime.now())
            })
            self.assertEqual(response.status_code, 200)
            res = json.loads(response.text)
            self.assertEqual(res['name'], 'test')

            res_id = res['id']
            response = service.invoke(api, sub_route='{}'.format(res_id))
            self.assertEqual(response.status_code, 200)
            res = json.loads(response.text)
            self.assertEqual(res['id'], res_id)

            response = service.invoke(
                api, 'delete', sub_route='{}'.format(res['id']))
            self.assertEqual(response.status_code, 200)

            response = service.invoke(api)
            self.assertEqual(response.status_code, 200)
            res = json.loads(response.text)
            self.assertEqual(len(res['test_entities']), 0)

        finally:
            server.stop()
            component_manager.boardcast('dispose', component_manager)
