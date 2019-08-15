#!/bin/bash
SETTING_PATH=basic_settings.py celery -A tasks worker --concurrency=32 --loglevel=info --logfile=log.txt
# celery -A tasks worker
