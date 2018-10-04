#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Benchmark Harness Controller
    This class is the main controller of the Benchmark Harness Application
    behaviour. It centralizes and distributes all calls to the different parts
    of the application. This is the entry point of the application as well.

    Usage: benchmark_controller.py --usage
"""

import sys
import os
import argparse
import subprocess
import re
import importlib
from pathlib import Path
import shutil

from helper.BenchmarkLogger import BenchmarkLogger
from helper.Manifest import Manifest

from models.compilers.CompilerFactory import CompilerFactory
from models.benchmarks.BenchmarkFactory import BenchmarkFactory
from models.machines.MachineFactory import MachineFactory

from executor.Execute import Execute
from executor.LinuxPerf import LinuxPerf
from executor.CompletedProcessList import CompletedProcessList

class BenchmarkController(object):
    """Point of entry of the benchmark harness application"""

    def __init__(self, argparse_parser, argparse_args):
        self.parser = argparse_parser
        self.args = argparse_args
        self.root_path = os.getcwd()
        self.logger = BenchmarkLogger(__name__, self.parser,
                                      self.args.verbose)

        self.logger.debug('Initial root path: %s' % self.args.root_path)
        self.unique_root_path = os.path.join(self.args.root_path,
                                             self.args.unique_id)
        self.logger.info('Unique root path: %s' % self.unique_root_path)

        self.logger.info('Benchmark Controller initialised')

    def _make_unique_name(self):
        """Unique name for the binary and results files"""

        # Format: bname - arch - compiler - flags - id
        sep = " - "
        identity = sep.join([
            self.args.benchmark_name,
            self.args.machine_type,
            (self.args.toolchain.rsplit('/', 1)[-1])[:24]])

        # Clean up invalid chars
        self.binary_name = re.sub("[^a-zA-Z0-9_-]+", "", identity).lower()

        self.logger.info('Unique name: %s' % identity)

    def _clean_path(self):
        """Cleanup the directory at the supplied root path"""

        # Always wipe everything
        if os.path.exists(self.unique_root_path):
            self.logger.info('Wiping %s' % self.unique_root_path)
            shutil.rmtree(self.unique_root_path)

        # Create the root path + results
        Path(self.unique_root_path).mkdir(parents=True, exist_ok=True)
        self.results_path = os.path.join(self.unique_root_path, 'results')
        os.mkdir(self.results_path)
        self.logger.debug('Results path: %s' % self.results_path)

    def _load_models(self):
        """Load compiler/benchmark/machine models"""

        try:
            # The benchmark is the only mandatory argument
            self.logger.debug('Benchmark model for %s' % self.args.benchmark_name)
            self.benchmark_model = BenchmarkFactory(self.args.benchmark_name,
                                                    self.unique_root_path).getBenchmark()
            self.logger.info('Benchmark model loaded')

            # Machine can be autodetected (if passed None to machine_type)
            self.machine_model = MachineFactory(self.args.machine_type).getMachine()
            if not self.args.machine_type:
                self.args.machine_type = self.machine_model.arch
            self.logger.debug('Machine model for %s' % self.args.machine_type)
            self.logger.info('Machine model loaded')

            # Compiler can be autodetected (if passed None to toolchain)
            self.compiler_model = CompilerFactory(self.args.toolchain,
                                                  self.unique_root_path).getCompiler()
            if not self.args.toolchain:
                self.args.toolchain = self.compiler_model.name
            self.logger.debug('Compiler model for %s' % self.args.toolchain)
            self.logger.info('Compiler model loaded')
        except ImportError as err:
            self.logger.error(err, True)
            raise

    def _run_all(self, list_of_commands, perf=False):
        """Runs and collects output results"""
        # TODO: We should add support for make and test parser plugins, too

        # Group all results in a single list object
        results = CompletedProcessList()

        if perf:
            self.logger.debug('Executing with Linux Perf engine')
            executor = LinuxPerf(plugin=self.benchmark_model.get_plugin(),
                                 affinity=self.machine_model.affinity)
        else:
            executor = Execute()

        for cmd in list_of_commands:
            if not cmd:
                self.logger.debug('Empty command, ignoring')
                continue

            # Executes command, captures results
            self.logger.info('Running command : ' + str(cmd))
            result = executor.run(cmd)
            results.append(result)

        return results

    def _check_results(self, results, public=False):
        out = results.stdout()
        err = results.stderr()
        ret = results.returncode

        if out and public:
            self.logger.info("Stdout:")
            self.logger.info(out)
        if err and public:
            self.logger.info("Stderr:")
            self.logger.info(err)

        if ret != 0:
            msg = "Execution error"
            if not public:
                msg += " " + err
            raise RuntimeError(msg)

    def _validate(self, result):
        """Validate the already parsed benchmark results"""

        if result and not isinstance(result, CompletedProcessList):
            raise TypeError('result should be a list')
        if result[0].stdout and not isinstance(result[0].stdout, dict):
            raise TypeError('result element should be a dict')

        for res in result:
            if not self.benchmark_model.validate(res.stdout):
                self.logger.error("Validation failed. Check output.")
                return False

        self.logger.info("Validation succeeded")
        return True

    def _output_logs(self, result):
        """Print out the results"""

        if result and not isinstance(result, CompletedProcessList):
            raise TypeError('result should be a list')
        if result[0].stdout and not isinstance(result[0].stdout, dict):
            raise TypeError('result element should be a dict')
        if result[0].stderr and not isinstance(result[0].stderr, dict):
            raise TypeError('result element should be a dict')

        # Print both stdout and stderr
        base_path = self.results_path + '/' + self.binary_name
        with open(base_path + '.out', 'w') as stdout:
            stdout.write(result.stdout())
            stdout.close()
        with open(base_path + '.err', 'w') as stderr:
            stderr.write(result.stderr())
            stderr.close()

        # Dump the manifest
        manifest = Manifest(self.benchmark_model,
                            self.compiler_model,
                            self.machine_model,
                            self.args, os.environ)
        manifest.dump(base_path + ".manifest")

        self.logger.info('Output logs at: %s.out'      % base_path)
        self.logger.info(' Error logs at: %s.err'      % base_path)
        self.logger.info('   Manifest at: %s.manifest' % base_path)

    def main(self):
        """Main driver - downloads, unzip, compile, run, collect results"""

        self._clean_path()

        self.logger.info(' ++ Loading Models (compiler/bench/machine) ++')
        self._load_models()

        self.logger.info(' ++ Preparing Environment ++')
        self._make_unique_name()

        self.logger.info(' ++ Preparing Benchmark Build ++')
        res = self._run_all(self.benchmark_model.prepare(self.machine_model,
                                                         self.compiler_model,
                                                         self.args.iterations,
                                                         self.args.size,
                                                         self.args.threads))
        self._check_results(res, public=True)

        self.logger.info(' ++ Building Benchmark ++')
        compiler_flags, linker_flags = self.compiler_model.get_flags()
        if self.args.compiler_flags:
            compiler_flags += " " + self.args.compiler_flags
        if self.args.linker_flags:
            linker_flags += " " + self.args.linker_flags
        res = self._run_all(self.benchmark_model.build(self.binary_name,
                                                       compiler_flags,
                                                       linker_flags))
        self._check_results(res, public=True)

        self.logger.info(' ++ Running Benchmark ++')
        res = self._run_all(self.benchmark_model.run(self.args.run_flags),
                               perf=True)
        self._check_results(res, public=False)

        self.logger.info(' ++ Validating Results ++')
        valid = self._validate(res)

        self.logger.info(' ++ Collecting Results / Manifest ++')
        self._output_logs(res)

        # Give "some" feedback if the log level is not high enough
        if (self.logger.silent()):
            if (valid):
                print("PASS")
            else:
                print("FAIL")

        return valid


if __name__ == '__main__':
    """This is the point of entry of our application, not much logic here"""
    parser = argparse.ArgumentParser(description='Benchmark Harness')

    # Required argument: benchmark name (must have a model implemented)
    parser.add_argument('benchmark_name', type=str,
                        help='The name of the benchmark to run')

    # Required, but auto-detected if omitted
    parser.add_argument('--machine_type', type=str,
                        help='The type of the machine to run the benchmark on')
    parser.add_argument('--toolchain', type=str,
                        help='The url/name of the toolchain to compile the benchmark')

    # Harness optionals
    parser.add_argument('--unique-id', type=str, default=str(os.getpid()),
                        help='Unique ID (ex. run number, sequential)')
    parser.add_argument('--root-path', type=str, default='./runs',
                        help='The root directory for toolchains, benchmarks, results')
    parser.add_argument('--iterations', type=int,
                        help='Number of iterations to run the same build')
    parser.add_argument('--size', type=int,
                        help='Meta variable that determines the size of the benchmark run')
    parser.add_argument('--threads', type=int,
                        help='Number of threads (OpenMP, multiple dispatch, MPI)')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='The verbosity of logging output')

    # Extra build/run flags
    parser.add_argument('--compiler-flags', type=str, default='',
                        help='The extra compiler flags')
    parser.add_argument('--linker-flags', type=str, default='',
                        help='The extra linker flags')
    parser.add_argument('--run-flags', type=str, default='',
                        help='The benchmark execution options')
    args = parser.parse_args()

    # Start the controller
    controller = BenchmarkController(parser, args)
    success = controller.main()
    if not success:
        sys.exit(1)
