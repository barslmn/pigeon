# -*- coding: utf-8 -*-
__author__ = 'bars'

import os
from pigeon import examples
from shutil import copyfile


def main():
    data_path = examples.__path__[0]
    cwd = os.getcwd()
    config_file = '/example.conf'
    copyfile(data_path + config_file, cwd + config_file)
