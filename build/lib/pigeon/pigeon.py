#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'bars'

import sys
import argparse
from pigeon.core.pipeline import Pipe
from pigeon.utils import copyexamplefiles
from pigeon import __version__


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--configfile', required=True,
                        default=None, type=str,
                        help='Config file for project. Please see documentation.')

    parser.add_argument('-d', '--dryrun', required=False, action='store_true',
                        help='Prints out commands to run to stdout without running them.')

    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='Write what is happening to stdout')

    parser.add_argument('--version',
                        action='version', version=__version__)

    subparsers = parser.add_subparsers(dest='tool')
    parser_example = subparsers.add_parser('createconfig',
                                           help='Create an example config file in current directory')

    args = parser.parse_args()
    return args


def main():
    if len(sys.argv) > 1:
        args = get_args()
        configfile = args.configfile
        dryrun = args.dryrun
        verbose = args.verbose
    else:
        sys.exit('"pigeon --help" for help')

    if args.tool == 'createconfig':
        copyexamplefiles.main()

    else:
        pipeline = Pipe(configfile, dryrun, verbose)
        pipeline.run_pipeline()
        pipeline.remove_files()


if __name__ == '__main__':
    main()
