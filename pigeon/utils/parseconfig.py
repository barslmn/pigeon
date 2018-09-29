# -*- coding: utf-8 -*-
__author__ = 'bars'

import configparser


class ParseConfig(object):

    """Docstring for ParseConfig. """

    def __init__(self, config_file):
        """TODO: to be defined1. """
        self.config_file = config_file

    @property
    def config(self):
        pipe_config = configparser.ConfigParser()
        pipe_config._interpolation = configparser.ExtendedInterpolation()
        pipe_config.read(self.config_file)
        return pipe_config

    @property
    def tool_list(self):
        tool_list = [tool for tool in self.config['PIPELINE']['pipeline'].split(' ')]
        return tool_list

    @property
    def tool_args(self):
        tool_args = {tool: {arg: self.config[tool][arg] for arg in list(
            self.config[tool])} for tool in self.tool_list}
        return tool_args

    @property
    def pipeline_args(self):
        return {arg: self.config['PIPELINE'][arg] for arg in self.config['PIPELINE']}

    @property
    def general_args(self):
        return {arg: self.config['GENERAL'][arg] for arg in self.config['GENERAL']}
