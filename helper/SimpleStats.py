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

        self.stdout = dict()
        self.stderr = dict()
        self._cluster_by_name(result)

    def _cluster_by_name(self, result):
        for res in result:
            if res.stdout['_name'] != res.stderr['_name']:
                raise ValueError("Binary names differ in out and err")
            name = res.stdout['_name']
            if name not in self.stdout:
                self.stdout[name] = list()
            self.stdout[name].append(res.stdout)
            if name not in self.stderr:
                self.stderr[name] = list()
            self.stderr[name].append(res.stderr)

    def _append_values(self, results):
        if not isinstance(results, list):
            raise TypeError('results should be a list')

        data = dict()
        for res in results:
            for key in res.keys():
                value = yaml.load(res[key])
                if isinstance(value, (int, float)):
                    if key not in data:
                        data[key] = []
                    data[key].append(value)
        return data

    def _collect_stats(self, data):
        stat = {'average': {}, 'deviation': {}, 'noise': {}}
        for key in data.keys():
            stat['average'][key] = statistics.mean(data[key])
            stat['deviation'][key] = statistics.stdev(data[key])
            # Noise level is the dimensionless coefficient of variation
            stat['noise'][key] = 0.0
            if stat['average'][key]:
                noise = (stat['deviation'][key]/stat['average'][key])*100
                stat['noise'][key] = float('%0.2f' % noise)
        return stat

    def dump(self, filename):
        stats = { 'out': dict(), 'err': dict() }
        for name, value in self.stdout.items():
            data = self._append_values(value)
            stats['out'][name] = self._collect_stats(data)
        for name, value in self.stderr.items():
            data = self._append_values(value)
            stats['err'][name] = self._collect_stats(data)

        with open(filename, 'w') as stdout:
            stdout.write(yaml.dump(stats, default_flow_style=False))
            stdout.close()
