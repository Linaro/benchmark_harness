#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Dumps out a manifest file, covering all data pertinent to the run.

    This should help automated tools to store the info in a database and
    query / pattern-match features together to find commonalities.
"""

from models.compilers.CompilerModel import CompilerModel
from models.benchmarks.BenchmarkModel import BenchmarkModel
from models.machines.MachineModel import MachineModel
import re
import yaml

class Manifest(object):
    def __init__(self, benchmark, compiler, machine, args=None, env=None):
        if not benchmark or not compiler or not machine:
            raise ValueError("Need all three objects to dump manifest")

        self.benchmark = benchmark
        self.compiler = compiler
        self.machine = machine
        self.args = args
        self.env = env

    def _clear_vars(self, module):
        """Clear up things that we don't want"""

        fields = dict()
        for name in vars(module):
            field = getattr(module,name)
            if field is None or isinstance(field, (str, int, float, list, tuple)):
                fields[name] = field
        return fields

    def _clear_env(self, env):
        """Clear up things that we don't want"""

        fields = dict()
        for key in env.keys():
            if key != '_' and \
               'PATH' not in key and \
               'USER' not in key and \
               'PWD' not in key and \
               'LANG' not in key and \
               'LC_' not in key and \
               'OMP' not in key and \
               'CC' not in key and \
               'CXX' not in key and \
               'FC' not in key and \
               'FLAGS' not in key:
                continue
            fields[key] = self.env[key]
        return fields

    def dump(self, filename):
        """Dump all info collected from all models"""

        manifest = dict()
        manifest['benchmark'] = self._clear_vars(self.benchmark)
        manifest['compiler'] = self._clear_vars(self.compiler)
        manifest['machine'] = self._clear_vars(self.machine)
        if self.args:
            manifest['args'] = self._clear_vars(self.args)
        if self.env:
            manifest['env'] = self._clear_env(self.env)

        with open(filename, 'w') as stdout:
            stdout.write(yaml.dump(manifest, default_flow_style=False))
            stdout.close()
