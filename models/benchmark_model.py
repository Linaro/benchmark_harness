#!/usr/bin/env python3

class BenchmarkModel(object):
    def __init__(self):
        self.base_runflags = ''
        self.base_compileflags = ''
        self.base_linkflags = ''
        self.base_deps = ''
        self.benchamrk_url = ''

    def prepare_benchmark(self, toolchain_url, extra_deps):
        """Prepares Environment for building and running the benchmark
        This entitles : installing dependencies, fetching the toolchain and
        the benchmark code in itself. Can use Ansible to do this platform
        independantly and idempotently"""

    def build_benchmark(self, extra_compileflags, extra_linkflags, binary_name):
        """Builds the benchmark using the base + extra flags"""

    def run_benchmark(self, extra_runflags, log_name):
        """Runs the benchmarks using the base + extra flags"""
