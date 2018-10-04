#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Dumps out some simple statistics about the results
"""

import yaml
import statistics

from executor.CompletedProcessList import CompletedProcessList

class SimpleStats(object):
    def __init__(self, result):
        if result and not isinstance(result, CompletedProcessList):
            raise TypeError('result should be a list')
        if result[0].stdout and not isinstance(result[0].stdout, dict):
            raise TypeError('result element should be a dict')
        if result[0].stderr and not isinstance(result[0].stderr, dict):
            raise TypeError('result element should be a dict')

        self.data = None
        self.stdout = []
        self.stderr = []
        for res in result:
            self.stdout.append(res.stdout)
            self.stderr.append(res.stderr)

    def _append_values(self, results):
        if not isinstance(results, list):
            raise TypeError('results should be a list')

        for res in results:
            for key in res.keys():
                value = yaml.load(res[key])
                if isinstance(value, (int, float)):
                    if key not in self.data:
                        self.data[key] = []
                    self.data[key].append(value)

    def dump(self, filename):
        self.data = dict()
        self._append_values(self.stdout)
        self._append_values(self.stderr)
        stat = {'average': {}, 'deviation': {}, 'noise': {}}
        for key in self.data.keys():
            stat['average'][key] = statistics.mean(self.data[key])
            stat['deviation'][key] = statistics.stdev(self.data[key])
            # Noise level is a comparable, dimensionless variation measure
            if stat['average'][key]:
                stat['noise'][key] = (stat['deviation'][key]/stat['average'][key])*100
            else:
                stat['noise'][key] = 0

        with open(filename, 'w') as stdout:
            stdout.write(yaml.dump(stat, default_flow_style=False))
            stdout.close()
