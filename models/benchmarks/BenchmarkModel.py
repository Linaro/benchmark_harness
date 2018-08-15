#!/usr/bin/env python3

import argparse
import os

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
        self.compiler = dict()

        # Benchmark files location
        self.url = ''
        self.root_path = ''

        # Harness options (meta variables) which may be unused
        self.iterations = 1
        self.size = 1

    ## CORE
    def prepare(self, root_path, compiler, iterations, size):
        """Prepares envrionment for running the benchmark
        This entitles : fetching the benchmark and preparing
        for running it"""
        if isinstance(root_path, str) and root_path:
            self.root_path = os.path.join(root_path, self.name)
        else:
            raise ValueError("Root path not passed to benchmark")
        if compiler:
            self.compiler = compiler
        else:
            raise ValueError("Compiler not passed to benchmark")

        if 'LD_LIBRARY_PATH' in os.environ:
            os.environ["LD_LIBRARY_PATH"] += ':' + compiler['lib']
        else:
            os.environ["LD_LIBRARY_PATH"] = compiler['lib']

        if isinstance(iterations, int) and iterations > 0:
            self.iterations = iterations
        if isinstance(size, int) and size > 0:
            self.size = size

    def build(self, binary_name, extra_compiler_flags, extra_linker_flags):
        all_compiler_flags = self.compiler_flags + " " + extra_compiler_flags
        all_linker_flags = self.linker_flags + " " + extra_linker_flags

        build_cmd = []
        make_cmd = []
        make_cmd.append('make')
        make_cmd.append('-C')
        make_cmd.append(self.root_path)
        make_cmd.append('CXX=' + self.compiler['cxx'])
        make_cmd.append('CC=' + self.compiler['cc'])
        make_cmd.append('FC=' + self.compiler['fortran'])
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

    ## HELPERS
    def get_parser(self):
        """Returns the plugin to parse the results"""
        pass
