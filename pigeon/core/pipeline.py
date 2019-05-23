import os
from os.path import splitext, basename, exists, join

import sys
import datetime
import configparser

from pigeon.utils.parseconfig import ParseConfig
from pigeon.utils.runpipe import RunPipe


class Pipe():

    """Docstring for seqPipe. """

    def __init__(self, pipeline_config, dryrun=False, verbose=False, read_from='file'):
        """TODO: to be defined1. """

        pipe_conf = ParseConfig(pipeline_config, read_from=read_from)
        self.project_parameters = pipe_conf.project_parameters
        self.task_parameters = pipe_conf.task_parameters
        self.task_list = pipe_conf.task_list
        self.runtime_task_list = pipe_conf.task_list

        self.include = pipe_conf.include
        self.number_included = 0

        # Use current working dir if not output_dir given
        if 'output_dir' in self.project_parameters:
            self.project_output_dir = os.path.abspath(self.project_parameters['output_dir'])
        else:
            self.project_output_dir = os.path.abspath(os.getcwd())

        if 'project_name' in self.project_parameters:
            self.project_name = self.project_parameters['project_name']
        else:
            self.project_name = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        self.cmd_feed = {}
        self.input_feed = {
            'input_files': self.project_parameters['input_files'].split()}

        if 'input_names' in self.project_parameters:
            self.input_names = {
                'input_names': self.project_parameters['input_names'].split()}

        self.dryrun = dryrun
        self.verbose = verbose
        self.create_pipeline()

    def in_out_feed(self, task, input_files):
        # Use task specific output_dir if given
        if 'output_dir' in self.task_parameters[task]:
            output_dir = self.task_parameters[task]['output_dir']
        else:
            output_dir = self.project_output_dir

        if 'dump_dir' in self.task_parameters[task]:
            dump_dir = self.task_parameters[task]['dump_dir']
            if self.dryrun is not True:
                mkdir(join(output_dir, dump_dir))
        else:
            dump_dir = ''

        if 'ext' in self.task_parameters[task]:
            ext = self.task_parameters[task]['ext']
        else:
            # keep it same
            if type(input_files) == list:
                ext = splitext(basename(input_files[0]))[1][1:]
            if type(input_files) == str:
                ext = splitext(basename(input_files))[1][1:]
        if 'suffix' in self.task_parameters[task]:
            suffix = self.task_parameters[task]['suffix']
        else:
            suffix = ''

        if 'input_multi' in self.task_parameters[task] and (self.task_parameters[task]['input_multi'] == 'paired' or self.task_parameters[task]['input_multi'] == 'all'):
            in_out = join(output_dir, dump_dir, splitext(
                basename(input_files[0]))[0] + suffix + '.' + ext)
        else:
            in_out = join(output_dir, dump_dir, splitext(
                basename(input_files))[0] + suffix + '.' + ext)

        # add newly created output files to input feed to be used by next task
        if 'paired_output' in self.task_parameters[task]:
            if task not in self.input_feed:
                self.input_feed[task] = [input_files, in_out]
            # if it exists append the output
            else:
                self.input_feed[task].extend([input_files, in_out])
        else:
            if task not in self.input_feed:
                self.input_feed[task] = [in_out]
            # if it exists append the output
            else:
                self.input_feed[task].append(in_out)

        return in_out

    def create_cmd(self, task, input_files, name=None):
        cmd = ''
        # if container task add container parameters
        if 'container' in self.task_parameters[task]:
            cmd = cmd + self.task_parameters[task]['container'] + ' '
        # otherwise just add path to task
        cmd = cmd + self.task_parameters[task]['tool']
        # if running sub command add the sub command
        if 'sub_tool' in self.task_parameters[task]:
            cmd = cmd + ' ' + self.task_parameters[task]['sub_tool']
        # add the parameters
        cmd = cmd + ' ' + self.task_parameters[task]['args']
        # If names true add names
        if 'named' in self.task_parameters[task]:
            cmd = cmd.replace('name_placeholder', name)
        # replace inputplaceholder with paired input files
        if 'input_multi' in self.task_parameters[task]:
            # replace input_file directory with task input_dir
            if 'input_dir' in self.task_parameters[task]:
                input_files = [join(self.task_parameters[task]['input_dir'], basename(input_file)) for input_file in input_files]
            if self.task_parameters[task]['input_multi'] == 'paired':
                # replace input_file directory with task input_dir
                if 'secondary_in_dir' in self.task_parameters[task]:
                    input_files[1] = join(self.task_parameters[task]['secondary_in_dir'], basename(input_files[1]))
                if 'secondary_input' in self.task_parameters[task]:
                    cmd = cmd.replace('input_placeholder', input_files[0])
                    cmd = cmd.replace(
                        'secondary_in_placeholder', input_files[1])
                else:
                    cmd = cmd.replace('input_placeholder',
                                      ' '.join(input_files))
            elif self.task_parameters[task]['input_multi'] == 'all':
                if 'input_flag_repeat' in self.task_parameters[task]:
                    flag_string = ' {} '.format(
                        self.task_parameters[task]['input_flag_repeat'])
                else:
                    flag_string = ' '
                cmd = cmd.replace('input_placeholder',
                                  flag_string.join(input_files))
        else:
            # replace input_file directory with task input_dir
            if 'input_dir' in self.task_parameters[task]:
                input_files = join(self.task_parameters[task]['input_dir'], basename(input_files))
            cmd = cmd.replace('input_placeholder', input_files)
        # replace output_placeholder with first file
        in_out = self.in_out_feed(task, input_files)
        cmd = cmd.replace('output_placeholder', in_out)

        if 'secondary_output' in self.task_parameters[task]:
            cmd = cmd.replace('secondary_out_placeholder',
                              self.secondary_output(task, input_files))

        return cmd

    def include_pipeline(self, include_task, i):
        task = include_task.split(':')[1]

        include_config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        include_config.read(self.include[task])

        for parameter in self.task_parameters[include_task]:
            include_config['PROJECT'][parameter] = self.task_parameters[include_task][parameter]
        include_config['PROJECT']['input_files'] = ' '.join(self.input_feed[self.task_parameters[include_task]['input_files']])
        pipeline = Pipe(include_config, self.dryrun, self.verbose, read_from='configparser')

        # add task parameters
        self.task_parameters.update(pipeline.task_parameters)

        # add commands to cmd_feed
        self.cmd_feed.update(pipeline.cmd_feed)

        # add pipeline output files to input_feed
        self.input_feed.update(pipeline.input_feed)
        # This binds pipes
        self.input_feed[include_task] = pipeline.input_feed[include_config['PROJECT']['output_files']]

        # add task cmds to list
        self.number_included += i
        self.runtime_task_list.pop(self.number_included)
        self.runtime_task_list[self.number_included:self.number_included] = pipeline.runtime_task_list

    def create_pipeline(self):
        for i, task in enumerate(self.task_list):
            if task.startswith('INCLUDE:'):
                self.include_pipeline(task, i)
                continue
            # For multiple input
            if 'input_multi' in self.task_parameters[task]:
                # For paired
                if self.task_parameters[task]['input_multi'] == 'paired':
                    # For paired and named
                    if 'named' in self.task_parameters[task]:
                        for name, input_files in zip(self.input_names['input_names'], chunks(self.input_feed[self.task_parameters[task]['input_from']], 2)):
                            if task not in self.cmd_feed:
                                self.cmd_feed[task] = [
                                    self.create_cmd(task, input_files, name)]
                            # if it exists append the output
                            else:
                                self.cmd_feed[task].append(
                                    self.create_cmd(task, input_files, name))
                    # Paired and not named
                    else:
                        for input_files in chunks(self.input_feed[self.task_parameters[task]['input_from']], 2):
                            if task not in self.cmd_feed:
                                self.cmd_feed[task] = [
                                    self.create_cmd(task, input_files)]
                            # if it exists append the output
                            else:
                                self.cmd_feed[task].append(
                                    self.create_cmd(task, input_files))

                # Can't name if input is all
                elif self.task_parameters[task]['input_multi'] == 'all':
                    self.cmd_feed[task] = [
                        self.create_cmd(task, self.input_feed[self.task_parameters[task]['input_from']])]

            else:
                # Single named input
                if 'named' in self.task_parameters[task]:
                    for name, input_file in zip(self.input_names['input_names'], self.input_feed[self.task_parameters[task]['input_from']]):
                        if task not in self.cmd_feed:
                            self.cmd_feed[task] = [
                                self.create_cmd(task, input_file, name)]
                        # if it exists append the output
                        else:
                            self.cmd_feed[task].append(
                                self.create_cmd(task, input_file, name))
                # Single Unnamed input
                else:
                    for input_file in self.input_feed[self.task_parameters[task]['input_from']]:
                        if task not in self.cmd_feed:
                            self.cmd_feed[task] = [
                                self.create_cmd(task, input_file)]
                        # if it exists append the output
                        else:
                            self.cmd_feed[task].append(
                                self.create_cmd(task, input_file))

    def run_pipeline(self):
        for task in self.runtime_task_list:
            for cmd in self.cmd_feed[task]:
                if self.dryrun is not True:
                    if 'pass' not in self.task_parameters[task]:
                        task_instance = RunPipe(
                            cmd, task, self.project_output_dir, self.project_name, self.verbose)
                        task_instance.run_task()
                    else:
                        pass
                else:
                    if 'pass' in self.task_parameters[task]:
                        sys.stdout.write('Passed:\n' + cmd + '\n')
                    else:
                        sys.stdout.write('\n' + cmd + '\n')
        self.remove_files()

    def remove_files(self):
        for task in self.runtime_task_list:
            if 'remove' in self.task_parameters[task] and self.task_parameters[task]['remove'] == 'True':
                for marked_for_removal in self.input_feed[task]:
                    if self.dryrun is True:
                        sys.stdout.write(
                            'Will be removed: {}\n'.format(marked_for_removal))
                    else:
                        os.remove(marked_for_removal)

    def secondary_output(self, task, input_files):
        # Use task specific output_dir if given
        if 'output_dir' in self.task_parameters[task]:
            output_dir = self.task_parameters[task]['output_dir']
        else:
            output_dir = self.project_output_dir

        if 'secondary_dump_dir' in self.task_parameters[task]:
            secondary_dump_dir = self.task_parameters[task]['secondary_dump_dir']
        elif 'dump_dir' in self.task_parameters[task]:
            secondary_dump_dir = self.task_parameters[task]['dump_dir']
        else:
            secondary_dump_dir = ''

        if self.dryrun is not True:
            mkdir(join(output_dir, secondary_dump_dir))
        if 'secondary_ext' in self.task_parameters[task]:
            secondary_ext = self.task_parameters[task]['secondary_ext']
        else:
            secondary_ext = ''
        if 'secondary_suffix' in self.task_parameters[task]:
            secondary_suffix = self.task_parameters[task]['secondary_suffix']
        else:
            secondary_suffix = ''
        if 'input_multi' in self.task_parameters[task] and (self.task_parameters[task]['input_multi'] == 'paired' or self.task_parameters[task]['input_multi'] == 'all'):
            secondary_out = join(output_dir, secondary_dump_dir, splitext(
                basename(input_files[0]))[0] + secondary_suffix + '.' + secondary_ext)
        else:
            secondary_out = join(output_dir, secondary_dump_dir, splitext(
                basename(input_files))[0] + secondary_suffix + '.' + secondary_ext)
        return secondary_out


def mkdir(directory):
    if not exists(directory):
        os.makedirs(directory)


def chunks(l, n):
    '''Yield successive n-size chunks from l.'''
    for i in range(0, len(l), n):
        yield l[i:i + n]
