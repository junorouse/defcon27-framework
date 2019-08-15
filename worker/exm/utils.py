#!/usr/bin/env python3
import re
import os
import json
import logging
import coloredlogs
import verboselogs
import traceback

from dhooks import Webhook, Embed

from exm.conf import settings

# logger = logging.getLogger(__name__)
logger = verboselogs.VerboseLogger(__name__)

# Coloredlogs docs :
# https://coloredlogs.readthedocs.io/en/latest/api.html#available-text-styles-and-colors
# https://coloredlogs.readthedocs.io/en/latest/api.html#classes-and-functions

formatter = '%(asctime)s %(funcName)15s : [%(levelname)s]  %(message)s'
# formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

level_styles = coloredlogs.DEFAULT_LEVEL_STYLES
level_styles.update({
    'debug': {'color': 'white'},
})

field_styles = coloredlogs.DEFAULT_FIELD_STYLES
field_styles.update({
    'asctime': {'color': 'blue', 'bright': True},
    'filename': {'color': 'magenta'},
    'funcName': {'color': 'magenta'},
    'lineno': {'color': 'magenta'},
})

coloredlogs.install(level='debug',
                    logger=logger,
                    milliseconds=True,
                    fmt=formatter,
                    level_styles=level_styles,
                    field_styles=field_styles)

# Add file handler
fh = logging.FileHandler('app.log')
fh.setLevel(logging.DEBUG)
ff = logging.Formatter(formatter)
fh.setFormatter(ff)
logger.addHandler(fh)


def flag_parser(data: str):
    # I am not sure, we need to change it at the table.
    return re.finditer(r'OOO[A-Za-z0-9 ]{45}', data)

def submit_flag(flag) -> bool:
    # I am not sure, we need to change it at the table.
    return True

def send_result_to_server(data):
    # TODO
    pass

def send_discord(level: str, message: str) -> bool:
    assert level in ['info', 'warning', 'success', 'error']
    try:
        hook = Webhook('https://discordapp.com/api/webhooks/607840984373526548/mh5iaiPW-y4M_cED3DfHQJL5h7nSg1K7PUP7pWGj8nKe9F0zpm3SFE3zEIzFX0TNGbMs')
    except:
        logger.exception('discord send error')
        return False

    if level == 'info':
        color = 0x00fffa
    elif level == 'warning':
        color = 0xffe900
    elif level == 'success':
        color = 0x04ff00
    elif level == 'error':
        color = 0xff0000

    try:
        embed = Embed(
            title=level.upper(),
            description=message,
            color=color,
            timestamp='now'  # sets the timestamp to current time
        )
        hook.send(embed=embed)
    except:
        logger.exception('discord send error')
        return False

    return True

def logging_and_discord(level: str, message: str):
    getattr(logger, level)(message)
    send_discord(level, message)

def get_configuration():
    conf_path = settings.CONF_PATH
    conf = json.loads(open(conf_path, 'rb').read())

    '''
    append exploit configuration
    '''
    challenges_directory = getattr(settings, 'CHALLENGES_DIRECTORY', './challenges/') # from config
    cfd = parse_challenges_from_directory()
    for chall in cfd:
        file_name = os.path.join(challenges_directory, chall, 'conf.json')
        if not os.path.exists(file_name): continue
        with open(file_name, 'r') as f:
            data = f.read()
            data = json.loads(data)
            conf['exploit'].append(data)

    return conf

def parse_challenges_from_directory():
    challenges_directory = getattr(settings, 'CHALLENGES_DIRECTORY', './challenges/') # from config
    return sorted(os.listdir(challenges_directory))

def parse_solvers_from_directory(challenge_name):
    challenges_directory = getattr(settings, 'CHALLENGES_DIRECTORY', './challenges/') # from config
    solvers = []

    for _ in os.scandir(os.path.join(challenges_directory, challenge_name)):
        if _.is_dir() and _.name.startswith('exploit') or _.name.startswith('ex'): # exploit folder prefix from config
            solvers.append(_.name)

    return solvers


if __name__ == '__main__':
    assert(next(flag_parser('asdfasdfsdfOOO{junoim123123123123}'))[0] == 'OOO{junoim123123123123}') # legacy
    challenges = parse_challenges_from_directory()
    solvers = parse_solvers_from_directory(challenges[0])
    print(solvers)
