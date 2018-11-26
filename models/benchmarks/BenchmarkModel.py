#!/usr/bin/env python3

import argparse
import os
import re

class BenchmarkModel(object):
    def __init__(self):
        # Benchmark name
        self.name = ''
        self.executable = ''

        # Build and execution flags
        self.compiler_flags = ''
        self.linker_flags = ''
        self.make_flags = ''
        self.run_flags = ''

        # Benchmark files location
        self.url = ''
        self.root_path = ''

        # Harness options (meta variables) which may be unused
        self.iterations = 1
        self.size = 1
        self.threads = 1

        # Machine and compiler models
        self.compiler = None
        self.machine = None

        # Validation checks dictionary (compare to results)
        self.checks = dict()

    ## CORE
    def prepare(self, machine, compiler, iterations, size, threads):
        """ Fetching the benchmark and preparing for running it"""

        if not machine or not compiler:
            raise ValueError("Machine/compiler models not passed to benchmark")

        self.machine = machine
        self.compiler = compiler

        libpath = self.compiler.get_env()['lib']
        if 'LD_LIBRARY_PATH' in os.environ:
            os.environ["LD_LIBRARY_PATH"] += ':' + libpath
        else:
            os.environ["LD_LIBRARY_PATH"] = libpath

        if iterations and iterations > 0:
            self.iterations = iterations
        if size and size > 0:
            self.size = size
        if threads and threads > 0:
            self.threads = threads

        prepare_cmds = []
        # If URL is a git repos, clone them
        is_git = re.search(r'\.git$', self.url)
        if is_git:
            prepare_cmds.append(['git', 'clone', self.url, self.root_path])
        # Else, let models override the behaviour
        return prepare_cmds


    def build(self, binary_name, extra_compiler_flags, extra_linker_flags):
        """Builds the benchmark"""

        all_compiler_flags = self.compiler_flags + " " + extra_compiler_flags
        all_linker_flags = self.linker_flags + " " + extra_linker_flags

        compiler_env = self.compiler.get_env()
        build_cmd = []
        make_cmd = []
        make_cmd.append('make')
        make_cmd.append('-C')
        make_cmd.append(self.root_path)
        make_cmd.append('CXX=' + compiler_env['cxx'])
        make_cmd.append('CC=' + compiler_env['cc'])
        make_cmd.append('FC=' + compiler_env['fc'])
        make_cmd.append('CFLAGS=' + all_compiler_flags)
        make_cmd.append('CXXFLAGS=' + all_compiler_flags)
        make_cmd.append('LDFLAGS=' + all_linker_flags)

        if self.make_flags:
            make_cmd.extend(self.make_flags.split())

        build_cmd.append(make_cmd)

        if isinstance(binary_name, str) and binary_name:
            build_cmd.append(['mv',
                              os.path.join(self.root_path, self.executable),
                              os.path.join(self.root_path, binary_name)])
            self.executable = binary_name

        return build_cmd

    def run(self, extra_run_flags):
        """Runs the benchmarks using the base + extra flags"""

        all_run_flags = self.run_flags + " " + extra_run_flags
        binary_path = os.path.join(self.root_path, self.executable)

        run_cmds = []
        for i in range(0, self.iterations):
            run_cmd = [binary_path]
            if all_run_flags:
                run_cmd.extend(all_run_flags.split())
            run_cmds.append(run_cmd)

        return run_cmds

    def validate(self, results):
        """Validate the run by investigating the results"""

        # Default cases
        if not self.checks:
            return True
        if not isinstance(results, dict):
            raise TypeError('Results must be dictionary to validate')

        # Check required fields' values
        for key in self.checks:
            if key not in results or not self.checks[key](results[key]):
                return False
        return True


    ## HELPERS
    def get_parser(self):
        """Returns the plugin to parse the results : specific benchmarks
           should override this method, returning their own parsers"""
        pass
