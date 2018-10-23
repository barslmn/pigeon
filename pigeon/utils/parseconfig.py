# -*- coding: utf-8 -*-
__author__ = 'bars'

import configparser


class ParseConfig(object):

    """Docstring for ParseConfig. """

    def __init__(self, pipeline_config, from_string=False):
        """TODO: to be defined1. """
        self.pipeline_config = pipeline_config
        self.from_string = from_string

    @property
    def config(self):
        _config = configparser.ConfigParser()
        _config._interpolation = configparser.ExtendedInterpolation()
        if self.from_string is not False:
            _config.read_string(self.pipeline_config)
        else:
            _config.read(self.pipeline_config)
        return _config

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
