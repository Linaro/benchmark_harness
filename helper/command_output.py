#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Command Output Structure
    This class serves as a data structure to contain the parsed (or not)
    results of the benchmark, the dictionary of parsed perf results of running
    the benchmark.
"""


class CommandOutput(object):
    def __init__(self):
        self.stdout_list = []
        self.stderr = []

    def add(self, stdout, perf_result):
        self.stdout_list += [stdout]
        self.stderr += [perf_result]

    def get(self, index):
        if (len(self.stdout_list) != len(self.stderr)):
            raise RuntimeError("Length of stdout and stderr do not match")
        return self.stdout_list[index], self.stderr[index]

    def get_list_out(self):
        return self.stdout_list

    def get_list_err(self):
        return self.stderr

    def len(self):
        return len(self.stderr)
