#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This class is an implementation of the BenchmarkModel interface
    (a python way of doing it, without decorations)

    It implements the actions necessary to prepare for the build, build,
    prepare for the run and run Lawrence Livermore National Laboratory
    Livermore Unstructured Lagrangian Explicit Shock Hydrodynamics (LULESH)
    benchmark.

"""

from models.benchmarks.BenchmarkModel import BenchmarkModel
from executor.Execute import OutputParser
import os
import argparse

class LuleshParser(OutputParser):
    """All data generated by lulesh as well as external dictionary"""
    def __init__(self):
        super().__init__()
        self.fields = {
            'ProblemSize' : r'Problem size\s+=\s+(\d+)',
            'IterationCount' : r'Iteration count\s+=\s+(\d+)',
            'FinalEnergy' : r'Final Origin Energy\s+=\s+(\d+[^\s]*)',
            'MaxAbsDiff' : r'MaxAbsDiff\s+=\s+(\d+[^\s]*)',
            'TotalAbsDiff' : r'TotalAbsDiff\s+=\s+(\d+[^\s]*)',
            'MaxRelDiff' : r'MaxRelDiff\s+=\s+(\d+[^\s]*)',
            'Elements' : r'Total number of elements:\s+(\d+)',
            'Threads' : r'Num threads: (\d+)',
            'Grind' : r'Grind time\(us\/z\/c\)\s+=\s+(\d+)',
            'FOM' : r'FOM\s+=\s+(\d+)'
        }


class ModelImplementation(BenchmarkModel):
    """This class is an implementation of the BenchmarkModel for LULESH"""

    def __init__(self):
        super().__init__()
        self.name = 'lulesh'
        self.executable = 'lulesh2.0'
        self.compiler_flags = '-DUSE_MPI=0 -fopenmp'
        self.linker_flags = '-fopenmp'
        self.size = 2
        self.benchmark_url = 'https://github.com/BaptisteGerondeau/LULESH.git'

    def prepare(self, root_path, compilers_dict, iterations, size):
        super().prepare(root_path, compilers_dict, iterations, size)

        # Lulesh specific flags based on options
        if (self.size >= 3):
            # Final Origin Energy: 1.482403e+06
            self.run_flags += '-s 90'
        elif (self.size == 2):
            # Final Origin Energy: 5.124778e+05
            self.run_flags += '-s 50'
        else:
            # Final Origin Energy: 2.720531e+04
            self.run_flags += '-s 10'

        prepare_cmds = []
        prepare_run_cmd = ['git', 'clone', self.benchmark_url, self.root_path]
        prepare_cmds.append(prepare_run_cmd)
        return prepare_cmds

    def get_plugin(self):
        """Returns the plugin to parse the results"""
        return LuleshParser()
