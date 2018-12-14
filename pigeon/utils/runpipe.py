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

    def __init__(self, cmd, tool, output_dir, project_name, verbose=False):
        self.cmd = cmd
        self.tool = tool
        self.output_dir = output_dir
        self.project_name = project_name
        self.verbose = verbose

    def run_cmd(self):
        def run_cmd_infra(orig_func):
            @wraps(orig_func)
            def wrapper(*args, **kwargs):
                tool_datetime = datetime.datetime.now().strftime("%A %Y/%m/%d %H:%M:%S %p")
                # Timing
                t1 = time.time()
                # Send cmd to shell
                cmd = orig_func(*args, **kwargs)
                tool_outs, tool_errs = Popen(
                    cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
                # Timing
                t2 = time.time() - t1
                # Loging
                logging.basicConfig(filename='{}.log'.format(
                    join(self.output_dir, self.project_name)), level=logging.INFO)
                logger = logging.getLogger(__name__)
                start_log = 'Start log for job: {}\nStart time: {}\nCommand:\n{}'.format(
                    self.tool, tool_datetime, self.cmd)
                end_log = 'Finished running command in {}.\nEnd of log for job: {}\n{}\n'.format(
                    t2, self.tool, '#'*20)

                # Log tool's stdout and stderr
                if len(tool_outs) > 1:
                    tool_outs = [tool_out for tool_out in tool_outs.decode(
                        'utf-8').split('\n') if len(tool_out) > 1]
                else:
                    tool_outs = ['Nothing here']
                if len(tool_errs) > 1:
                    tool_errs = [tool_err for tool_err in tool_errs.decode(
                        'utf-8').split('\n') if len(tool_err) > 1]
                else:
                    tool_errs = ['Nothing here']

                logger.info(start_log)
                for tool_out in tool_outs:
                    logger.info(tool_out)
                for tool_err in tool_errs:
                    logger.error(tool_err)
                logger.info(end_log)

                if self.verbose != False:
                    sys.stdout.write('{}\nTOOL OUTPUT:\n{}\nTOOL ERROR:\n{}\n{}'.format(
                        start_log, '\n'.join(tool_outs), '\n'.join(tool_errs), end_log))
                return orig_func(*args, **kwargs)
            return wrapper
        return run_cmd_infra

    def run_tool(self):
        @self.run_cmd()
        def run_tool_infra():
            return self.cmd
        return run_tool_infra()
