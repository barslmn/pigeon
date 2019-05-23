# -*- coding: utf-8 -*-
__author__ = 'bars'

import configparser


class ParseConfig(object):

    """Docstring for ParseConfig. """

    def __init__(self, pipeline_config, read_from='file'):
        """TODO: to be defined1. """
        self.pipeline_config = pipeline_config
        self.read_from = read_from

    @property
    def config(self):
        if self.read_from == 'configparser':
            _config = self.pipeline_config
        else:
            _config = configparser.ConfigParser(
                interpolation=configparser.ExtendedInterpolation()
            )
            if self.read_from == 'string':
                _config.read_string(self.pipeline_config)
            else:
                _config.read(self.pipeline_config)
        return _config

    @property
    def project_parameters(self):
        return {parameter: self.config['PROJECT'][parameter] for parameter in self.config['PROJECT']}

    @property
    def task_list(self):
        task_list = [task for task in self.config['PIPELINE']
                     ['pipeline'].replace('\n', ' ').split()]
        return task_list

    @property
    def task_parameters(self):
        task_parameters = {task: {parameter: self.config[task][parameter].replace('\n', ' ') for parameter in list(self.config[task])} for task in self.task_list}
        return task_parameters

    @property
    def include(self):
        if 'INCLUDE' in self.config.keys():
            return {pipeline: self.config['INCLUDE'][pipeline] for pipeline in self.config['INCLUDE']}
        else:
            pass
