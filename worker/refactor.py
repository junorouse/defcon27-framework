#!/usr/bin/env python3
import re
import time
import datetime
import traceback

from tasks import run

from exm import utils
from exm.utils import logger
from exm.conf import settings

from pprint import pprint
from apscheduler.schedulers.blocking import BlockingScheduler


"""
input:
{
    "team_info": [
        {"name": "PPP", "host": "1.2.3.4"},
        {"name": "QQQ", "host": "1.2.3.4"},
    ],
    "exploit": [
        {
            "name": "prob1",
            "port": 1234,
            "teams": [
                    {"name": "PPP", "priority": [{"name": "ex1", "max_try": 5}]},
                    {
                        "name": "QQQ", 
                        "priority": [
                                        {"name": "ex2", "max_try": 5}, 
                                        {"name": "ex1", "max_try": 5}
                                    ]
                    }
            ]
        }
    ]
}
"""


class ExploitManager:
    def __init__(self):
        self.configuration = None
        self.CHALLENGES = None
        self.TEAM_INFO = None

        self.reload_configuration()

    def reload_configuration(self):
        self.configuration = utils.get_configuration()
        pprint(self.configuration)
        self.CHALLENGES = utils.parse_challenges_from_directory()
        self.TEAM_INFO = self.configuration['team_info']
        self.EXPLOITS = self.configuration['exploit']

    def setup_task_list(self, only_me=None, reload_conf=False) -> (list, int):
        if reload_conf:
            self.reload_configuration()

        commands = []
        task_count = 0

        for exploit in self.EXPLOITS:
            challenge_name = exploit['name']
            challenge_port = exploit['port']

            if challenge_name in self.CHALLENGES:
                challenge_solvers = utils.parse_solvers_from_directory(challenge_name)
                challenges = []

                not_exists = set([])
                for team in exploit['teams']:
                    exploits = []

                    for _exploit in team['priority']:
                        if only_me is not None:
                            if (challenge_name, _exploit['name']) not in only_me:
                                continue
                        else:
                            if 'is_test' in _exploit and _exploit['is_test']:
                                continue

                        if _exploit['name'] in challenge_solvers:
                            host = ''
                            exploits.append({
                                'cmd': ['/usr/bin/timeout', '15', settings.CHALLENGES_DIRECTORY + f'./{challenge_name}/{_exploit["name"]}/run.sh'],
                                'host': [asdf for asdf in self.TEAM_INFO if asdf['name'] == team['name']][0]['host'],
                                'name': _exploit['name'],
                                'max_try': _exploit['max_try'],
                                'now_try': 0,
                                'output': None,
                                'celery': None,
                                'status': None
                            })
                            task_count += 1
                        else:
                            # logger.warning(f'`{challenge_name}` -> `{team["name"]}` -> `{_exploit["name"]}` exploit not exists')
                            not_exists.add(f'`{challenge_name}` -> `{_exploit["name"]}` exploit not exists')
                    
                    challenges.append({
                        'team': team['name'],
                        'exploits': exploits,
                        'status': None
                    })

                commands.append({
                    'challenge': challenge_name,
                    'port': challenge_port,
                    'tasks': challenges,
                    'status': None
                })
            else:
                # logger.warning('challenge not exists')
                not_exists.add(f'`{challenge_name}` challenge  not exists')

            if not_exists:
                utils.logging_and_discord('warning', '\n'.join(not_exists))

        return commands, task_count
    
    def start_exploit(self, tasks: list) -> list:
        """
        `result.append(exploit)` mean it's end of each exploit 
        """
        def make_result(challenge: dict, task: dict, exploit: dict) -> dict:
            """
            {
                "challenge": "prob1",
                "flag": "OOO{123123123123123adsf}",
                "max_try": 5,
                "now_try": 1,
                "status": 1,
                "team": "PPP"
            }
            """
            if exploit['status'] == 'success':
                # TODO: submit flag to authentication server / append response
                _flag = exploit['output']
                _flag_output = utils.submit_flag(_flag)
            else:
                _flag_output = None

            return {
                'challenge': challenge['challenge'],
                'team': task['team'],
                'exploit': exploit['name'],
                'output': exploit['output'],
                'flag_status': _flag_output,
                'max_try': exploit['max_try'],
                'now_try': exploit['now_try'],
                'status': exploit['status'],
                'date': str(datetime.datetime.now())
            }

        result = []

        # run exploit
        for challenge in tasks:
            for task in challenge['tasks']:
                for exploit in task['exploits']:
                    if exploit['status'] is None:
                        obj = run.delay(exploit['cmd'], exploit['host'])
                        # create celery task
                        exploit['celery'] = obj
                        exploit['status'] = 'progress'
                        exploit['now_try'] += 1
                        logger.info(f'[!] execute `{exploit["name"]}` exploit of `{challenge["challenge"]}` to team {task["team"]} '+
                              f'with retry ({exploit["now_try"]} / {exploit["max_try"]})')
                        break
                    elif exploit['status'] == 'progress':
                        # check exploit finished
                        if exploit['celery'].ready():
                            try:
                                ret = exploit['celery'].get()
                            except:
                                # traceback.print_exc()
                                # error
                                traceback_log = exploit['celery'].traceback
                                exploit['output'] = traceback_log[:100]
                                # if exception occur, don't retry
                                exploit['status'] = 'exception'
                                result.append(make_result(challenge, task, exploit))
                            else:
                                # success
                                output = ret[0]
                                try:
                                    flag = next(utils.flag_parser(ret[1]))[0]
                                except StopIteration:
                                    # flag not found, do retry
                                    if exploit['now_try'] == exploit['max_try']:
                                        exploit['status'] = 'retry_exceed'
                                        result.append(make_result(challenge, task, exploit))
                                    else:
                                        exploit['status'] = None
                                        break
                                else:
                                    exploit['output'] = flag
                                    exploit['status'] = 'success'
                                    result.append(make_result(challenge, task, exploit))
                        else:
                            break
                    elif exploit['status'] == 'success':
                        pass
                    else:
                        # failed case
                        # exception, timeout, retry_exceed
                        pass

        return result

    def start_round(self, only_me=None):
        logger.info('=====================================================')
        logger.info(f'round start : {datetime.datetime.now()}')

        tasks, task_count = self.setup_task_list(only_me=only_me, reload_conf=True)

        if task_count == 0:
            logger.warning('nothing to work!')

        finish_task = 0
        result = []

        while task_count > finish_task:
            partial_result = self.start_exploit(tasks)
            finish_task += len(partial_result)

            if len(partial_result) != 0:
                result.extend(partial_result)
                logger.info(partial_result)
                logger.info(f'finished : {finish_task} / remain : {task_count - finish_task}')

                time.sleep(0.3)

        # TODO : send result to Dashboard

        # send to logger
        success_message = []
        warning_message = []
        error_message = []
        for res in result:
            msg = f'`{res["challenge"]}` -> `{res["team"]}`'
            if res['status'] == 'success':
                # should be get flag
                msg += f' -> `{res["exploit"]}` exploit success.'

                # TODO: submit flag to authentication server / append response
                _flag = res['output']
                if res['flag_status']:
                    # utils.logging_and_discord('success', msg + f' and submit flag success -> {_flag}')
                    success_message.append(msg + f' and submit flag success -> {_flag}')
                else:
                    logger.exception(f'error while submitting flag ({_flag}) to authentication server')
                    # utils.send_discord('warning', msg + f' but submit flag failed -> {_flag}')
                    warning_message.append(msg + f' but submit flag failed -> {_flag}')
            else:
                # utils.logging_and_discord('error', msg + f' -> `{res["exploit"]}` exploit failed ({res["status"]})')
                error_message.append(msg + f' -> `{res["exploit"]}` exploit failed ({res["status"]})')

        if success_message:
            for i in range(0, len(success_message), 8):
                utils.logging_and_discord('success', '\n'.join(success_message[i: i+8]))
        if warning_message:
            for i in range(0, len(warning_message), 5):
                utils.logging_and_discord('warning', '\n'.join(warning_message[i: i+5]))
        if error_message:
            for i in range(0, len(error_message), 5):
                utils.logging_and_discord('error', '\n'.join(error_message[i: i+5]))

        logger.info('~~~~~~~~~~~~~~~~~~~~end~~~~~~~~~~~~~~~~~~~'*2)

    def run(self):
        # run schuduler
        now = datetime.datetime.utcnow()
        logger.info(f'UTC Now : {now}')

        # round start every 5 minute
        round_interval = 2
        
        nearest_minute = int((now.minute + round_interval - 1) / round_interval) * round_interval
        next_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=nearest_minute)
        interval = {'weeks': 0, 'days': 0, 'hours': 0, 'minutes': round_interval, 'seconds': 0}

        logger.info(f'Start time : {next_time}')

        self.start_round()

        scheduler = BlockingScheduler()
        scheduler.add_job(func=self.start_round, args=(),
                          start_date=next_time.strftime('%Y-%m-%d %H:%M:%S'),
                          trigger='interval', **interval)
        scheduler.start()


if __name__ == '__main__':
    exm = ExploitManager()
    exm.run()
