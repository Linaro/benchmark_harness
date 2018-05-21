#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import coloredlogs

class BenchmarkLogger(object):
    def __init__(self, logger, parser, verbosity):
        self.logger = logger
        coloredlogs.install(level = max(30 - verbosity*10, 0),
                            logger=self.logger)
        self.parser = parser

    def error(self, err, print_help=False):
        self.logger.info(err)
        if print_help:
            print('\n\n')
            self.parser.print_help()

    def warning(self, warning):
        self.logger.warning(warning)

    def info(self, info):
        self.logger.info(info)

    def debug(self, trace):
        self.logger.debug(trace)

