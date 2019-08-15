#!/usr/bin/env python3.7

from celery import Celery
import time
import os
import signal
from exm.conf import settings
import subprocess

CELERY_PATH = getattr(settings, 'CELERY_PATH')
app = Celery('tasks', broker=CELERY_PATH, backend=CELERY_PATH)

@app.task
def run(args, host):
    new_env = os.environ.copy()
    new_env['TARGET_HOST'] = host
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=new_env)

    try:
        outs, errs = proc.communicate(timeout=30)
    except:
        proc.kill()
        outs, errs = proc.communicate()
    finally:
        if type(outs) == bytes:
            outs = outs.decode('utf-8')
        if type(errs) == bytes:
            errs = errs.decode('utf-8')
        return (args, outs, errs)


