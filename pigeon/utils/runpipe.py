# -*- coding: utf-8 -*-

__author__ = 'bars'

import sys
import time
import logging
import datetime
from os.path import join
from functools import wraps
from subprocess import Popen, PIPE


class RunPipe:

    def __init__(self, cmd, task, output_dir, project_name, verbose=False):
        self.cmd = cmd
        self.task = task
        self.output_dir = output_dir
        self.project_name = project_name
        self.verbose = verbose

    def run_cmd(self):
        def run_cmd_infra(orig_func):
            @wraps(orig_func)
            def wrapper(*args, **kwargs):
                task_datetime = datetime.datetime.now().strftime("%A %Y/%m/%d %H:%M:%S %p")
                # Timing
                t1 = time.time()
                # Send cmd to shell
                cmd = orig_func(*args, **kwargs)
                task_outs, task_errs = Popen(
                    cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
                # Timing
                t2 = time.time() - t1
                # Loging
                logging.basicConfig(filename='{}.log'.format(
                    join(self.output_dir, self.project_name)), level=logging.INFO)
                logger = logging.getLogger(__name__)
                start_log = 'Start log for job: {}\nStart time: {}\nCommand:\n{}'.format(
                    self.task, task_datetime, self.cmd)
                end_log = 'Finished running command in {}.\nEnd of log for job: {}\n{}\n'.format(
                    t2, self.task, '#' * 20)

                # Log task's stdout and stderr
                if len(task_outs) > 1:
                    task_outs = [task_out for task_out in task_outs.decode(
                        'utf-8').split('\n') if len(task_out) > 1]
                else:
                    task_outs = ['Nothing here']
                if len(task_errs) > 1:
                    task_errs = [task_err for task_err in task_errs.decode(
                        'utf-8').split('\n') if len(task_err) > 1]
                else:
                    task_errs = ['Nothing here']

                logger.info(start_log)
                for task_out in task_outs:
                    logger.info(task_out)
                for task_err in task_errs:
                    logger.error(task_err)
                logger.info(end_log)

                if not self.verbose:
                    sys.stdout.write('{}\nTOOL OUTPUT:\n{}\nTOOL ERROR:\n{}\n{}'.format(
                        start_log, '\n'.join(task_outs), '\n'.join(task_errs), end_log))
                return orig_func(*args, **kwargs)
            return wrapper
        return run_cmd_infra

    def run_task(self):
        @self.run_cmd()
        def run_task_infra():
            return self.cmd
        return run_task_infra()
