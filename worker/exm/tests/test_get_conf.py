import unittest

import os
import json

os.environ['CONF_PATH'] = '/tmp/test_conf.json'

from exm.conf import settings
from exm.utils import get_configuration


class TestGetConfig(unittest.TestCase):
    """
    Test get config
    """

    def test_get_conf(self):
        data = json.dumps({'juno': '1234'})
        open('/tmp/test_conf.json', 'wb').write(data.encode())
        self.assertEqual(get_configuration()['juno'], '1234')


if __name__ == '__main__':
    unittest.main()
