#!/usr/bin/env python3


class BenchmarkModel(object):
    def __init__(self):
        self.name = 'default'
        self.base_runflags = ''
        self.base_compileflags = ''
        self.base_linkflags = ''
        self.base_build_deps = ''
        self.base_run_deps = ''
        self.benchamrk_url = ''

    def prepare_build_benchmark(self, extra_deps):
        """Prepares Environment for building the benchmark
        This entitles : installing dependencies for build"""
        pass

    def prepare_run_benchmark(self, extra_deps):
        """Prepares envrionment for running the benchmark
        This entitles : fetching the benchmark and preparing
        for running it"""
        pass

    def fetch_flags(self):
        return self.base_compileflags, self.base_linkflags

    def build_benchmark(self, complete_compile_flags, complete_link_flags, binary_name):
        """Builds the benchmark using the complete flags"""
        pass

    def run_benchmark(self, extra_runflags):
        """Runs the benchmarks using the base + extra flags"""
        pass
