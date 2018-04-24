#!/usr/bin/env python3

from models.benchmarks.benchmark_model import BenchmarkModel
import os

class BenchmarkModelImplementation(BenchmarkModel):
    """This class is an implementation of the BenchmarkModel for LULESH"""

    def __init__(self):
        super().__init__()
        self.name = 'lulesh'
        self.base_runflags = ''
        self.base_compileflags = '-DUSE_MPI=0 -fopenmp'
        self.base_linkflags = '-O3 -fopenmp'
        self.base_build_deps = ''
        self.base_run_deps = ''
        self.benchmark_url = 'https://github.com/BaptisteGerondeau/LULESH.git'

    def prepare_build_benchmark(self, extra_deps):
        """Prepares Environment for building and running the benchmark
        This entitles : installing dependencies, fetching benchmark code
        Can use Ansible to do this platform independantly and idempotently"""
        prepare_cmds = []
        prepare_run_cmd = ['git', 'clone', self.benchmark_url, self.name]
        prepare_cmds.append(prepare_run_cmd)
        return prepare_cmds

    def prepare_run_benchmark(self, extra_deps):
        """Prepares envrionment for running the benchmark
        This entitles : fetching the benchmark and preparing
        for running it"""
        prepare_cmds = []
        prepare_run_cmd = []
        prepare_cmds.append(prepare_run_cmd)
        return prepare_cmds

    def build_benchmark(self, compiler, complete_compile_flags, complete_link_flags, binary_name):
        """Builds the benchmark using the base + extra flags"""
        build_cmd = []
        make_cmd = []
        make_cmd.append('make')
        make_cmd.append('CXX=' + compiler)
        make_cmd.append('CXXFLAGS=' + complete_compile_flags)
        make_cmd.append('LDFLAGS=' + complete_link_flags)
        make_cmd.append('LULESH_EXEC="' + binary_name + '"')
        build_cmd.append(make_cmd)
        return build_cmd

    def run_benchmark(self, binary_name, extra_runflags):
        """Runs the benchmarks using the base + extra flags"""
        binary_path = os.path.join(os.getcwd(), binary_name)
        run_cmd = [binary_path, extra_runflags]
        return run_cmd


# if args.name.lower() in BENCHMARK_LIST:
#    subprocess.run(['mkdir', identity])
#    with cd(identity):
#        subprocess.run(['git', 'clone', GIT_URLS[args.name.lower()], args.name.lower()], check=True)
#        with cd(args.name.lower()):
#            subprocess.run(make_cmd, check=True)
#            with open(report_name, 'w') as fd:
#                subprocess.check_call(['./' + execname, args.benchmark_options],
#                        stderr=subprocess.STDOUT, stdout=fd)
