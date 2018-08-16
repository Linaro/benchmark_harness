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
import shutil

from helper.BenchmarkLogger import BenchmarkLogger
from helper.CommandOutput import CommandOutput

from models.compilers.CompilerFactory import CompilerFactory
from models.benchmarks.BenchmarkFactory import BenchmarkFactory
from models.machines.MachineFactory import MachineFactory
from executor.Execute import Execute
from executor.LinuxPerf import LinuxPerf


class BenchmarkController(object):
    """Point of entry of the benchmark harness application"""

    def __init__(self, argparse_parser, argparse_args):
        self.parser = argparse_parser
        self.args = argparse_args
        self.root_path = os.getcwd()
        self.logger = BenchmarkLogger(logging.getLogger(__name__), self.parser,
                                      self.args.verbose)

        self._auto_detect()

        self._make_unique_name()

        self.logger.info('Benchmark Controller initialised')

    def _auto_detect(self):
        """Detect machine_type and compiler if empty"""
        if not self.args.machine_type:
            out, err = Execute(['uname', '-m']).run()
            if err:
                msg = "'uname -m' error: [" + err + "]"
                raise RuntimeError("Error auto-detecting machine type: " + msg)
            if not out:
                raise RuntimeError("Unable to detect machine type with uname")
            self.args.machine_type = out.strip()
            self.logger.info('Autodetected arch: %s' % self.args.machine_type)

        if not self.args.toolchain:
            for comp in ['gcc', 'clang']:
                out, err = Execute(['which', comp]).run()
                if err or not out:
                    continue
                self.args.toolchain = comp
                self.logger.info('Autodetected compiler: %s' % comp)
                return

            if not self.args.toolchain:
                raise RuntimeError("Error auto-detecting compiler: " + err)

    def _make_unique_name(self):
        """Unique name for the binary and results files"""

        # Format: bname - arch - compiler - flags - id
        sep = " - "
        identity = sep.join([
            self.args.name,
            self.args.machine_type,
            (self.args.toolchain.rsplit('/', 1)[-1])[:24],
            self.args.compiler_flags,
            self.args.benchmark_options,
            repr(self.args.unique_id)])

        # Clean up invalid chars
        self.binary_name = re.sub("[^a-zA-Z0-9_-]+", "", identity).lower()

        self.logger.info('Unique name: %s' % identity)

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
        base_path = self.results_path + '/' + self.binary_name
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
        self.logger.info('Unique root path: %s' % self.unique_root_path)

        # If wipe, remove everything
        if self.args.wipe and os.path.exists(self.unique_root_path):
            self.logger.info('Wiping %s' % self.unique_root_path)
            shutil.rmtree(self.unique_root_path)

        # Now, create the whole tree
        Path(self.unique_root_path).mkdir(parents=True, exist_ok=True)

        self.compiler_path = os.path.join(self.unique_root_path, 'compiler')
        os.mkdir(self.compiler_path)
        self.logger.debug('Compiler path: %s' % self.compiler_path)

        self.benchmark_path = os.path.join(self.unique_root_path, 'benchmark')
        os.mkdir(self.benchmark_path)
        self.logger.debug('Benchmark path: %s' % self.benchmark_path)

        self.results_path = os.path.join(self.unique_root_path, 'results')
        os.mkdir(self.results_path)
        self.logger.debug('Results path: %s' % self.results_path)

    def _load_models(self):
        """Load compiler/benchmark/machine models"""

        try:
            self.logger.debug('Benchmark model for %s' % self.args.name)
            self.benchmark_model = BenchmarkFactory(self.args.name).getBenchmark()
            self.benchmark_model.set_path(os.path.abspath(self.benchmark_path))
            self.logger.info('Benchmark model loaded')

            self.logger.debug('Machine model for %s' % self.args.machine_type)
            self.machine_model = MachineFactory(self.args.machine_type).getMachine()
            self.logger.info('Machine model loaded')

            self.logger.debug('Compiler model for %s' % self.args.toolchain)
            self.logger.debug('     compiler_path %s' % self.compiler_path)
            compiler_factory = CompilerFactory(self.args.toolchain,
                                               self.compiler_path)
            self.compiler_model = compiler_factory.getCompiler()
            self.logger.info('Compiler model loaded')
        except ImportError as err:
            self.logger.error(err, True)
            raise

        self._build_complete_flags()

    def _run_all(self, list_of_commands, perf=False):
        """Runs and collects output results"""
        # TODO: We should add support for make and test parser plugins, too

        # Group all outputs in a single list object
        output = CommandOutput()

        for cmd in list_of_commands:
            if not cmd:
                self.logger.debug('Empty command, ignoring')
                continue

            if perf:
                self.logger.debug('Executing with Linux Perf engine')
                executor = LinuxPerf(cmd, self.benchmark_model.get_plugin())
            else:
                executor = Execute(cmd)

            # Executes command, captures outputs
            self.logger.info('Running command : ' + str(cmd))
            stdout, stderr = executor.run()
            output.add(stdout, stderr)

            # Show outputs if not parsed, assuming this isn't benchmark results
            if isinstance(stdout, str):
                self.logger.info("Stdout:")
                self.logger.info(stdout)
            if isinstance(stderr, str):
                self.logger.info("Stderr:")
                self.logger.info(stderr)

            self.logger.info('Execution complete')

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

    # Required argument: benchmark name (must have a model implemented)
    parser.add_argument('name', metavar='benchmark_name', type=str,
                        help='The name of the benchmark to run')

    # Harness optional: root dir, unique id, verbose
    parser.add_argument('--machine_type', type=str,
                        help='The type of the machine to run the benchmark on')
    parser.add_argument('--toolchain', type=str,
                        help='The url/name of the toolchain to compile the benchmark')
    parser.add_argument('--unique-id', type=str, default=os.getpid(),
                        help='Unique ID (ex. run number, sequential)')
    parser.add_argument('--wipe', type=bool, default=False,
                        help='Wipe benchmark root directory before run')
    parser.add_argument('--benchmark-root', type=str, default='./runs',
                        help='The benchmark root directory')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='The verbosity of logging output')

    # Extra flags
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
    args = parser.parse_args()

    # Start the controller
    controller = BenchmarkController(parser, args)
    controller.main()
