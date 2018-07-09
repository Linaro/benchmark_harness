#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Benchmark Harness Controller
    This class is the main controller of the Benchmark Harness Application
    behaviour. It centralizes and distributes all calls to the different parts
    of the application. This is the entry point of the application as well.

    Usage: benchmark_controller.py --usage
"""

import os
import argparse
import subprocess
import re
import importlib
import yaml
import logging
import coloredlogs
from pathlib import Path

from helper.compiler_factory import CompilerFactory
from helper.model_loader import ModelLoader
from helper.benchmark_logger import BenchmarkLogger
from helper.command_output import CommandOutput

from models.compilers.compiler_model import CompilerModel
from models.benchmarks.benchmark_model import BenchmarkModel
from models.machines.machine_model import MachineModel
from executor.execute import run
from executor.linux_perf import *


class BenchmarkController(object):
    """Point of entry of the benchmark harness application"""

    def __init__(self, argparse_parser, argparse_args):
        self.parser = argparse_parser
        self.args = argparse_args
        self.root_path = os.getcwd()
        self.logger = BenchmarkLogger(logging.getLogger(__name__), self.parser,
                                      self.args.verbose)
        self._make_unique_name()

        self.logger.info('Benchmark Controller initialised')

    def _make_unique_name(self):
        """Unique name for the binary and results files"""

        identity = str(
            self.args.name + '_' +
            (self.args.toolchain.rsplit('/', 1)[-1])[:24] + '_' +
            self.args.compiler_flags.replace(" ", "") + '_' +
            self.args.machine_type + '_' +
            self.args.benchmark_options.replace(" ", ""))

        self.binary_name = re.sub("[^a-zA-Z0-9_]+", "", identity).lower()
        self.report_name = identity

        self.logger.info('Unique name: %s' % self.report_name)

    def _build_complete_flags(self):
        """Joins all cpmopile and link flags from all sources into one"""

        if self.compiler_model is None or \
           self.benchmark_model is None or \
           self.machine_model is None:
            self.logger.warning('No models loaded! Not trying to build flags')
            return

        # Compiler specific flags
        build_flags, link_flags = self.compiler_model.get_flags()
        self.complete_build_flags = build_flags
        self.complete_link_flags = link_flags
        self.logger.debug('Toolchain specific build flags: %s' % build_flags)
        self.logger.debug('Toolchain specific link flags: %s' % link_flags)

        # Machine specific flags
        build_flags, link_flags = self.machine_model.get_flags()
        self.complete_build_flags += ' ' + build_flags
        self.complete_link_flags += ' ' + link_flags
        self.logger.debug('Machine specific build flags: %s' % build_flags)
        self.logger.debug('Machine specific link flags: %s' % link_flags)

        # Benchmark specific flags
        build_flags, link_flags = self.benchmark_model.get_flags()
        self.complete_build_flags += ' ' + build_flags
        self.complete_link_flags += ' ' + link_flags
        self.logger.debug('Benchmark specific build flags: %s' % build_flags)
        self.logger.debug('Benchmark specific link flags: %s' % link_flags)

        # Validate flags (based on compiler)
        build_flags, link_flags = self.compiler_model.validate_flags(
            self.complete_build_flags, self.complete_link_flags)

        self.complete_build_flags = build_flags
        self.complete_link_flags = link_flags

        self.logger.info('Build flags: %s' % self.complete_build_flags)
        self.logger.info('Link flags: %s' % self.complete_link_flags)

    def _output_logs(self, benchmark_output):
        """Print out the results"""

        out = benchmark_output.get_list_out()
        err = benchmark_output.get_list_err()

        # Make sure we have the right type of results
        # Must be a list of either str or dict
        if out and not \
           (isinstance(out[0], str) or isinstance(out[0], dict)):
            raise TypeError('out should be a list of string or dict')
        if err and not \
           (isinstance(err[0], str) or isinstance(err[0], dict)):
            raise TypeError('err should be a list of string or dict')
        if not os.path.isdir(self.results_path):
            raise TypeError('%s should be a directory' % self.results_path)

        # Print both stdout and stderr
        base_path = self.results_path + '/' + self.report_name
        with open(base_path + '.out', 'w') as stdout:
            yaml.dump(out, stdout, default_flow_style=False)
        with open(base_path + '.err', 'w') as stderr:
            yaml.dump(err, stderr, default_flow_style=False)

        self.logger.info('Output logs at: %s.out' % base_path)
        self.logger.info(' Error logs at: %s.err' % base_path)

    def _make_dirs(self):
        """Create the directory at the supplied benchmark root"""

        self.logger.debug('Initial root path: %s' % self.args.benchmark_root)
        self.logger.debug('Binary name: %s' % self.binary_name)
        self.unique_root_path = os.path.join(self.args.benchmark_root,
                                             self.binary_name)
        os.mkdir(self.unique_root_path)
        self.logger.info('Unique root path: %s' % self.unique_root_path)

        self.compiler_path = os.path.join(self.unique_root_path, 'compiler/')
        os.mkdir(self.compiler_path)
        self.logger.debug('Compiler path: %s' % self.compiler_path)

        self.benchmark_path = os.path.join(self.unique_root_path, 'benchmark/')
        os.mkdir(self.benchmark_path)
        self.logger.debug('Benchmark path: %s' % self.benchmark_path)

        self.results_path = os.path.join(self.unique_root_path, 'results/')
        os.mkdir(self.results_path)
        self.logger.debug('Results path: %s' % self.results_path)

    def _load_models(self):
        """Load compiler/benchmark/machine models"""

        try:
            # TODO: We may want to create factories for benchmark and machine
            self.logger.debug('Benchmark model for %s' % self.args.name)
            self.benchmark_model = ModelLoader(self.args.name + '_model.py',
                                               'benchmark',
                                               self.root_path).load()
            self.benchmark_model.set_path(os.path.abspath(self.benchmark_path))
            self.logger.info('Benchmark model loaded')

            self.logger.debug('Machine model for %s' % self.args.machine_type)
            self.machine_model = ModelLoader(self.args.machine_type + '_model.py',
                                             'machine',
                                             self.root_path).load()
            self.logger.info('Machine model loaded')

            self.logger.debug('Compiler model for %s' % self.args.toolchain)
            self.logger.debug('     compiler_path %s' % self.compiler_path)
            compiler_factory = CompilerFactory(self.args.toolchain,
                                               self.args.sftp_user,
                                               self.compiler_path)
            self.compiler_model = compiler_factory.getCompiler()
            self.logger.info('Compiler model loaded')
        except ImportError as err:
            self.logger.error(err, True)

        self._build_complete_flags()

    def _run_all(self, list_of_commands, perf=False):
        """Runs and collects output and perf results (from stderr)"""

        output = CommandOutput()

        for cmd in list_of_commands:
            if not cmd:
                self.logger.debug('Empty command, ignoring')
                continue

            self.logger.info('Running command : ' + str(cmd))
            # TODO: Make sure we don't have a special case for perf
            # This should be transparent to the user
            if perf:
                # Passing benchmark plugin for stdout parsing
                self.logger.debug('Executing with Linux Perf engine')

                perf_parser = LinuxPerf(cmd, self.benchmark_model.get_plugin())
                stdout, stderr = perf_parser.stat()
            else:
                stdout, stderr = run(cmd)
                self.logger.info(stdout)

            output.add(stdout, stderr)
            self.logger.info('Execution complete. Output added to the list')

        return output

    def main(self):
        """Main driver - downloads, unzip, compile, run, collect results"""

        self.logger.info(' ++ Preparing Environment ++')
        self._make_dirs()

        self.logger.info(' ++ Loading Models (compiler/bench/machine) ++')
        self._load_models()

        self.logger.info(' ++ Preparing Benchmark Build ++')
        self._run_all(self.benchmark_model.prepare_build_benchmark(self.args.benchmark_build_deps))

        self.logger.info(' ++ Building Benchmark ++')
        self._run_all(self.benchmark_model.build_benchmark(self.compiler_model.getDictCompilers(),
                                                           self.complete_build_flags,
                                                           self.complete_link_flags,
                                                           self.binary_name,
                                                           self.args.benchmark_build_vars))

        self.logger.info(' ++ Preparing Execution ++')
        self._run_all(self.benchmark_model.prepare_run_benchmark(self.args.benchmark_run_deps,
                                                                 self.compiler_model.getDictCompilers()))

        self.logger.info(' ++ Running Benchmark ++')
        benchmark_output = self._run_all(self.benchmark_model.run_benchmark(self.binary_name,
                                                                               self.args.benchmark_options), perf=True)

        self.logger.info(' ++ Collecting Results ++')
        self._output_logs(benchmark_output)

        return 0


if __name__ == '__main__':
    """This is the point of entry of our application, not much logic here"""
    parser = argparse.ArgumentParser(description='Benchmark Harness')
    parser.add_argument('name', metavar='benchmark_name', type=str,
                        help='The name of the benchmark to run')
    parser.add_argument('machine_type', type=str,
                        help='The type of the machine to run the benchmark on')
    parser.add_argument('toolchain', type=str,
                        help='The url/name of the toolchain to compile the benchmark')
    parser.add_argument('--sftp-user', type=str, default='',
                        help='The sftp user to connect to the sftp server with')
    parser.add_argument('--compiler-flags', type=str, default='',
                        help='The extra compiler flags')
    parser.add_argument('--link-flags', type=str, default='',
                        help='The extra link flags')
    parser.add_argument('--benchmark-build-vars', type=str, default='',
                        help='The extra values the benchmark build needs (e.g. MODEL for Himeno')
    parser.add_argument('--benchmark-options', type=str, default='',
                        help='The benchmark options')
    parser.add_argument('--benchmark-build-deps', type=str, default='',
                        help='The benchmark specific extra dependencies for the build')
    parser.add_argument('--benchmark-run-deps', type=str, default='',
                        help='The benchmark specific extra dependencies for the run')
    parser.add_argument('--benchmark-root', type=str, required=True,
                        help='The benchmark root directory')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='The verbosity of logging output')
    args = parser.parse_args()

    controller = BenchmarkController(parser, args)
    controller.main()
