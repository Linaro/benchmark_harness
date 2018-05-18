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

from models.benchmarks.benchmark_model import BenchmarkModel
from executor.execute import *
import os

class ModelImplementation(BenchmarkModel):
    """This class is an implementation of the BenchmarkModel for LULESH"""

    def __init__(self):
        super().__init__()
        self.name = 'himeno'
        self.base_runflags = ''
        self.base_compileflags = ''
        self.base_linkflags = '-O3'
        self.base_build_deps = ''
        self.base_run_deps = ''
        self.benchmark_url = 'http://accc.riken.jp/en/wp-content/uploads/sites/2/2015/07/himenobmt.c.zip'

    def prepare_build_benchmark(self, extra_deps):
        """Prepares Environment for building and running the benchmark
        This entitles : installing dependencies, fetching benchmark code
        Can use Ansible to do this platform independantly and idempotently"""
        prepare_cmds = [[]]
        prepare_cmds.append(['mkdir', self.name])
        prepare_cmds.append(['wget', '-P', self.name , self.benchmark_url])
        prepare_cmds.append(['unzip', self.name + '/himenobmt.c.zip', '-d', self.name])
        prepare_cmds.append(['lhasa', '-xw=' + self.name, './' + self.name + '/himenobmt.c.lzh'])
        return prepare_cmds

    def prepare_run_benchmark(self, extra_deps):
        """Prepares envrionment for running the benchmark
        This entitles : fetching the benchmark and preparing
        for running it"""
        prepare_cmds = [[]]
        prepare_run_cmd = []
        prepare_cmds.append(prepare_run_cmd)
        return prepare_cmds

    def build_benchmark(self, compilers_dict, complete_compile_flags,
                        complete_link_flags, binary_name, benchmark_build_vars):
        """Builds the benchmark using the base + extra flags"""
        if benchmark_build_vars == '':
            benchmark_build_vars = 'MODEL=SMALL'
        build_cmd = [[]]
        make_cmd = []
        make_cmd.append('make')
        make_cmd.append('CXX=' + compilers_dict['cxx'])
        make_cmd.append('CC=' + compilers_dict['cc'])
        make_cmd.append('FC=' + compilers_dict['fortran'])
        make_cmd.append('CFLAGS=' + complete_compile_flags)
        make_cmd.append('LDFLAGS=' + complete_link_flags)
        make_cmd.append(benchmark_build_vars)
        build_cmd.append(make_cmd)
        return build_cmd

    def run_benchmark(self, binary_name, extra_runflags):
        """Runs the benchmarks using the base + extra flags"""
        binary_name = 'bmt'
        binary_path = os.path.join(os.getcwd(), binary_name)
        if extra_runflags is None or extra_runflags == '':
            run_cmd = [binary_path]
        else:
            run_cmd = [binary_path, extra_runflags]
        return run_cmd

    def get_plugin(self):
        """Returns the plugin to parse the results"""
        pass
