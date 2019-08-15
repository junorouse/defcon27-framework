import os

CHALLENGES_DIRECTORY = './challenges/'
CELERY_PATH = 'redis://localhost/'
DATABASES = ''
CONF_PATH = os.getenv('CONF_PATH') or './conf_example.json'
DEBUG = True
