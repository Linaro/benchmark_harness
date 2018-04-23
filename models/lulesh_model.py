#!/usr/bin/env python3

from models.benchmark_model import BenchmarkModel

class BenchmarkModelImplementation(BenchmarkModel):
    """This class is an implementation of the BenchmarkModel for LULESH"""
    def __init__(self):
        self.base_runflags = ''
        self.base_compileflags = ''
        self.base_linkflags = ''
        self.base_deps = 'build-essential'
        self.benchmark_url = 'https://github.com/LLNL/LULESH.git'

    def prepare_benchmark(self, toolchain_url, extra_deps):
        """Prepares Environment for building and running the benchmark
        This entitles : installing dependencies, fetching the toolchain and
        the benchmark code in itself. Can use Ansible to do this platform
        independantly and idempotently"""

    def build_benchmark(self, extra_compileflags, extra_linkflags, binary_name):
        """Builds the benchmark using the base + extra flags"""
        make_cmd = []
        make_cmd += 'make'
#        make_cmd += 'CXX=' + self.compiler
        make_cmd += 'CXXFLAGS=' + self.base_compileflags + ' ' + extra_compileflags
        make_cmd += 'LDFLAGS=' + self.base_linkflags + ' ' + extra_linkflags
        make_cmd += 'LULESH_EXEC="' + binary_name + '"'

    def run_benchmark(self, extra_runflags, log_name):
        """Runs the benchmarks using the base + extra flags"""
        print(self.benchmark_url, flush=True)


#if args.name.lower() in BENCHMARK_LIST:
#    subprocess.run(['mkdir', identity])
#    with cd(identity):
#        subprocess.run(['git', 'clone', GIT_URLS[args.name.lower()], args.name.lower()], check=True)
#        with cd(args.name.lower()):
#            subprocess.run(make_cmd, check=True)
#            with open(report_name, 'w') as fd:
#                subprocess.check_call(['./' + execname, args.benchmark_options],
#                        stderr=subprocess.STDOUT, stdout=fd)
