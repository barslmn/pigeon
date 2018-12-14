import sys
import os
from os.path import splitext, basename, exists, join
from pigeon.utils.parseconfig import ParseConfig
from pigeon.utils.runpipe import RunPipe


class Pipe():

    """Docstring for seqPipe. """

    def __init__(self, pipeline_config, dryrun=False, verbose=False , read_from='file'):
        """TODO: to be defined1. """

        pipe_configs = ParseConfig(pipeline_config, read_from=read_from)
        self.general_args = pipe_configs.general_args
        self.tool_args = pipe_configs.tool_args
        self.tool_list = pipe_configs.tool_list
        self.project_name = self.general_args['project_name']
        self.output_dir = join(
            self.general_args['output_dir'], self.general_args['project_name'])

        self.cmd_feed = {}
        self.input_feed = {
            'input_files': self.general_args['input_files'].split(' ')}

        if 'input_names' in self.general_args.keys():
            self.input_names = {
                'input_names': self.general_args['input_names'].split(' ')}

        self.dryrun = dryrun
        self.verbose = verbose
        self.create_pipeline()

    def in_out_feed(self, tool, input_files):

        if 'dump_dir' in self.tool_args[tool].keys():
            dump_dir = self.tool_args[tool]['dump_dir']
            if self.dryrun is not True:
                mkdir(join(self.output_dir, dump_dir))
        else:
            dump_dir = ''

        if 'ext' in self.tool_args[tool].keys():
            ext = self.tool_args[tool]['ext']
        else:
            ext = ''
        if 'suffix' in self.tool_args[tool].keys():
            suffix = self.tool_args[tool]['suffix']
        else:
            suffix = ''

        if 'input_multi' in self.tool_args[tool].keys() and (self.tool_args[tool]['input_multi'] == 'paired' or self.tool_args[tool]['input_multi'] == 'all'):
            in_out = join(self.output_dir, dump_dir, splitext(
                basename(input_files[0]))[0] + suffix + '.' + ext)
        else:
            in_out = join(self.output_dir, dump_dir, splitext(
                basename(input_files))[0] + suffix + '.' + ext)

        # add newly created output files to input feed to be used by next tool
        if 'paired_output' in self.tool_args[tool].keys():
            if tool not in self.input_feed.keys():
                self.input_feed[tool] = [input_files, in_out]
            # if it exists append the output
            else:
                self.input_feed[tool].extend([input_files, in_out])
        else:
            if tool not in self.input_feed.keys():
                self.input_feed[tool] = [in_out]
            # if it exists append the output
            else:
                self.input_feed[tool].append(in_out)

        return in_out

    def create_cmd(self, tool, input_files, name=None):
        cmd = ''
        # if java tool add java -jar to start
        if 'java' in self.tool_args[tool].keys():
            cmd = cmd + self.tool_args[tool]['java'] + ' -jar '
        # otherwise just add path to tool
        cmd = cmd + self.tool_args[tool]['tool']
        # if running sub command add the sub command
        if 'sub_tool' in self.tool_args[tool].keys():
            cmd = cmd + ' ' + self.tool_args[tool]['sub_tool']
        # add the args
        cmd = cmd + ' ' + self.tool_args[tool]['args']
        # If names true add names
        if 'named' in self.tool_args[tool].keys():
            cmd = cmd.replace('name_placeholder', name)
        # replace inputplaceholder with paired input files
        if 'input_multi' in self.tool_args[tool].keys():
            if self.tool_args[tool]['input_multi'] == 'paired':
                if 'secondary_in_placeholder' in self.tool_args[tool].keys():
                    cmd = cmd.replace('input_placeholder', input_files[0])
                    cmd = cmd.replace(
                        'secondary_in_placeholder', input_files[1])
                else:
                    cmd = cmd.replace('input_placeholder',
                                      ' '.join(input_files))
            elif self.tool_args[tool]['input_multi'] == 'all':
                if 'input_flag_repeat' in self.tool_args[tool].keys():
                    flag_string = ' {} '.format(
                        self.tool_args[tool]['input_flag_repeat'])
                else:
                    flag_string = ' '
                cmd = cmd.replace('input_placeholder',
                                  flag_string.join(input_files))
        else:
            cmd = cmd.replace('input_placeholder', input_files)
        # replace output_placeholder with first file
        in_out = self.in_out_feed(tool, input_files)
        cmd = cmd.replace('output_placeholder', in_out)

        if 'secondary_output' in self.tool_args[tool].keys():
            cmd = cmd.replace('secondary_out_placeholder',
                              self.secondary_output(tool, input_files))

        return cmd

    def create_pipeline(self):
        for tool in self.tool_list:
            # For multiple input
            if 'input_multi' in self.tool_args[tool].keys():
                # For paired
                if self.tool_args[tool]['input_multi'] == 'paired':
                    # For paired and named
                    if 'named' in self.tool_args[tool].keys():
                        for name, input_files in zip(self.input_names['input_names'], chunks(self.input_feed[self.tool_args[tool]['input_from']], 2)):
                            if tool not in self.cmd_feed.keys():
                                self.cmd_feed[tool] = [
                                    self.create_cmd(tool, input_files, name)]
                            # if it exists append the output
                            else:
                                self.cmd_feed[tool].append(
                                    self.create_cmd(tool, input_files, name))
                    # Paired and not named
                    else:
                        for input_files in chunks(self.input_feed[self.tool_args[tool]['input_from']], 2):
                            if tool not in self.cmd_feed.keys():
                                self.cmd_feed[tool] = [
                                    self.create_cmd(tool, input_files)]
                            # if it exists append the output
                            else:
                                self.cmd_feed[tool].append(
                                    self.create_cmd(tool, input_files))

                # Can't name if input is all
                elif self.tool_args[tool]['input_multi'] == 'all':
                    self.cmd_feed[tool] = [
                        self.create_cmd(tool, self.input_feed[self.tool_args[tool]['input_from']])]

            else:
                # Single named input
                if 'named' in self.tool_args[tool].keys():
                    for name, input_file in zip(self.input_names['input_names'], self.input_feed[self.tool_args[tool]['input_from']]):
                        if tool not in self.cmd_feed.keys():
                            self.cmd_feed[tool] = [
                                self.create_cmd(tool, input_file, name)]
                        # if it exists append the output
                        else:
                            self.cmd_feed[tool].append(
                                self.create_cmd(tool, input_file, name))
                # Single Unnamed input
                else:
                    for input_file in self.input_feed[self.tool_args[tool]['input_from']]:
                        if tool not in self.cmd_feed.keys():
                            self.cmd_feed[tool] = [
                                self.create_cmd(tool, input_file)]
                        # if it exists append the output
                        else:
                            self.cmd_feed[tool].append(
                                self.create_cmd(tool, input_file))

    def run_pipeline(self):
        for tool in self.tool_list:
            for cmd in self.cmd_feed[tool]:
                if self.dryrun is not True:
                    mkdir(self.output_dir)
                    if 'pass' not in self.tool_args[tool].keys():
                        tool_instance = RunPipe(
                            cmd, tool, self.output_dir, self.project_name, self.verbose)
                        tool_instance.run_tool()
                    else:
                        pass
                else:
                    if 'pass' in self.tool_args[tool].keys():
                        sys.stdout.write('Passed:\n' + cmd + '\n')
                    else:
                        sys.stdout.write('\n' + cmd + '\n')
        self.remove_files()

    def remove_files(self):
        for tool in self.tool_list:
            if 'remove' in self.tool_args[tool].keys() and self.tool_args[tool]['remove'] == 'True':
                for marked_for_removal in self.input_feed[tool]:
                    if self.dryrun is True:
                        sys.stdout.write(
                            'Will be removed: {}'.format(marked_for_removal))
                    else:
                        os.remove(marked_for_removal)

    def secondary_output(self, tool, input_files):
        if 'secondary_dump_dir' in self.tool_args[tool].keys():
            secondary_dump_dir = self.tool_args[tool]['secondary_dump_dir']
        else:
            secondary_dump_dir = ''
        if self.dryrun is not True:
            mkdir(join(self.output_dir, secondary_dump_dir))
        if 'secondary_ext' in self.tool_args[tool].keys():
            secondary_ext = self.tool_args[tool]['secondary_ext']
        else:
            secondary_ext = ''
        if 'secondary_suffix' in self.tool_args[tool].keys():
            secondary_suffix = self.tool_args[tool]['secondary_suffix']
        else:
            secondary_suffix = ''
        if 'input_multi' in self.tool_args[tool].keys() and (self.tool_args[tool]['input_multi'] == 'paired' or self.tool_args[tool]['input_multi'] == 'all'):
            secondary_out = join(self.output_dir, secondary_dump_dir, splitext(
                basename(input_files[0]))[0] + secondary_suffix + '.' + secondary_ext)
        else:
            secondary_out = join(self.output_dir, secondary_dump_dir, splitext(
                basename(input_files))[0] + secondary_suffix + '.' + secondary_ext)
        return secondary_out


def mkdir(directory):
    if not exists(directory):
        os.makedirs(directory)


def chunks(l, n):
    '''Yield successive n-size chunks from l.'''
    for i in range(0, len(l), n):
        yield l[i:i + n]
