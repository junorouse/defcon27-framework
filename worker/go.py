#!/usr/bin/env python3
import re
import time

from tasks import run

from exm.utils import *
from exm.conf import settings

from pprint import pprint


cmd_list = []

'''
1. parse team info
2. parse exploit schedule info
3. run, run!

[CELARY WORKER]
prob1 -> PPP - ex1..
      -> QQQ - ex2..
      -> WWW - ex3..

MAX_TRY,

'''

def log(*args):
    if settings.DEBUG:
        pprint(args)

exploit_conf = get_configuration()
pprint(exploit_conf)

CHALLENGS = parse_challenges_from_directory()
TEAM_INFO = exploit_conf['team_info']

for chall_name , v in exploit_conf['exploit'].items():
    if chall_name  in CHALLENGS:
        # TOOD: multi processing starts from here
        challenge_port = v.pop('PORT')
        challenge_exploits = parse_solvers_from_directory(chall_name)
        log(challenge_exploits)

        for team, exploits in v.items():
            log(team, exploits)
            # print(team, exploits, TEAM_INFO[team])
            print('-'*20)
            tmp = []
            for exploit in exploits:
                tmp.append({'task': ['/usr/bin/timeout', '3', settings.CHALLENGES_DIRECTORY + './%s/%s/run.sh' % (chall_name, exploit['name'])],
                            'max_try': exploit['MAX_TRY'], 'team': team, 'challenge': chall_name})

            cmd_list.append(tmp)


# stdbuf -i0 -o0 -e0
'''
use buffer to 0 ori PYTHONUNBUFFERED=1
'''

'''
cmd_list = [
        # ["stdbuf", "-i0", "-o0", "-e0", "/usr/bin/timeout", "3", "./example_chall/run.sh"],
        ["/usr/bin/timeout", "3", settings.CHALLENGES_DIRECTORY + "./example_chall/exploit1/run.sh"],
    ]
'''

def is_done(t_array):
    for _ in t_array:
        if _['status'] == 0:
            return False
    return True

def get_idx_t_array(t_array, t):
    for i in range(len(t_array)):
        if t_array[i] == t:
            return i
    return -1
    

def main():
    pprint(cmd_list)
    t_array = []

    # TODO: Performance
    for cmd in cmd_list:
        t_array.append({'task': run.delay(cmd[0]['task']), 'status': 0, 'next_cmd': cmd[1:], 'now_try': 0, 'max_try': cmd[0]['max_try'],
            'team': cmd[0]['team'], 'challenge': cmd[0]['challenge']})

    while True:
        if is_done(t_array): break

        for t in t_array:
            if t['task'].ready() and t['status'] == 0:
                idx = get_idx_t_array(t_array, t)
                t_array[idx]['now_try'] += 1

                try:
                    # success
                    ret = t['task'].get()
                    output = ret[0]
                    flag = next(flag_parser(ret[1]))[0]

                    t_array[idx]['status'] = 1
                    t_array[idx]['flag'] = flag
                except:
                    # err
                    print(dir(t['task']))
                    print('err', t['task'].traceback)
                    print('------------========='*5)
                    print(t_array[idx]['next_cmd'])

                    if t_array[idx]['max_try'] == t_array[idx]['now_try']:
                        # change to next exploit
                        t_array[idx]['status'] = -1
                        _cmd = t_array[idx]['next_cmd']
                        if len(_cmd) == 0:
                            break
                        t_array.append({'task': run.delay(_cmd[0]['task']), 'status': 0, 'next_cmd': _cmd[1:], 'now_try': 0, 'max_try': _cmd[0]['max_try'],
                            'team': _cmd[0]['team'], 'challenge': _cmd[0]['challenge']})

                finally:
                    print('idx', idx)

        time.sleep(0.1)

    # clean up

    for i in range(len(t_array)):
        t_array[i].pop('next_cmd')
        t_array[i].pop('task')

    print('='*50)
    print(json.dumps(t_array, sort_keys=True,
            indent=4, separators=(',', ': ')))

if __name__ == '__main__':
    main()
