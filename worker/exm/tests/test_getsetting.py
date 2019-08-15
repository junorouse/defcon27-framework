import unittest

import os
from exm.conf import settings


class TestGetSetting(unittest.TestCase):
    """
    Test get config
    """

    def test_getenv_setting_path(self):
        self.assertEqual(os.getenv('SETTING_PATH') != '', True)

    def test_get_CELERY_PATH(self):
        self.assertEqual(settings.CELERY_PATH.startswith('redis://'), True)


if __name__ == '__main__':
    unittest.main()
