#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This class is an implementation of the BenchmarkModel interface
    (a python way of doing it, without decorations)

    It implements the actions necessary to prepare for the build, build,
    prepare for the run and run OpenBLAS's benchmarks + BLAS-Tester

"""

from models.benchmarks.BenchmarkModel import BenchmarkModel
from executor.Execute import OutputParser
import os

class OpenBLASParser(OutputParser):
    """All data generated by himeno as well as external dictionary"""

    def __init__(self):
        super().__init__()
        self.fields = {
            'Test0': r'\s+0\s.*\d+\.\d\s+(\d+\.\d\d)\s+PASS',
            'Test1': r'\s+1\s.*\d+\.\d\s+(\d+\.\d\d)\s+PASS',
            'Test2': r'\s+2\s.*\d+\.\d\s+(\d+\.\d\d)\s+PASS',
            'Test3': r'\s+3\s.*\d+\.\d\s+(\d+\.\d\d)\s+PASS',
            'Test4': r'\s+4\s.*\d+\.\d\s+(\d+\.\d\d)\s+PASS',
            'Test5': r'\s+5\s.*\d+\.\d\s+(\d+\.\d\d)\s+PASS',
            'Test6': r'\s+6\s.*\d+\.\d\s+(\d+\.\d\d)\s+PASS',
            'Test7': r'\s+7\s.*\d+\.\d\s+(\d+\.\d\d)\s+PASS',
            'Test8': r'\s+8\s.*\d+\.\d\s+(\d+\.\d\d)\s+PASS',
            'Test9': r'\s+9\s.*\d+\.\d\s+(\d+\.\d\d)\s+PASS',
            'Pass': r'tests run, (\d+) passed'
        }

class ModelImplementation(BenchmarkModel):
    """This class is an implementation of the BenchmarkModel for OpenBLAS"""

    def __init__(self):
        super().__init__()
        self.name = 'openblas'
        self.urls = ['https://github.com/xianyi/OpenBLAS.git',
                     'https://github.com/xianyi/BLAS-Tester.git']
        for t in ['c', 'd', 's', 'z']:
            for s in ['1', '2', '3']:
                self.executables.append("BLAS-Tester/bin/x"+t+"l"+s+"blastst")

    def prepare(self, machine, compiler, iterations, size, threads):
        prepare_cmds = super().prepare(machine, compiler, iterations, size, 1)
        # TODO: Choose options form arguments
        blaslib = os.path.join(os.path.realpath(self.root_path), 'OpenBLAS', 'libopenblas.a')
        arch = "ARM64"
        if self.machine.arch == 'x86_64':
            arch = "X86"
        self.make_flags = {
            'OpenBLAS': 'USE_THREAD=0',
            'BLAS-Tester': '-j NUMTHREADS=1 ARCH='+arch+' TEST_BLAS='+blaslib
        }

        return prepare_cmds

    def get_plugin(self):
        """Returns the plugin to parse the results"""
        return OpenBLASParser()
