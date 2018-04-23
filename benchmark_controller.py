#!/usr/bin/env python3

import os
import argparse
import subprocess
import re
import importlib
from pathlib import Path

class BenchmarkController(object):
    def __init__(self, argparse_parser, argparse_args):
        self.parser = argparse_parser
        self.args = argparse_args

    def _load_benchmark_model(self, benchmark_name):
        mod = importlib.import_module('models.' + benchmark_name)
        return mod.BenchmarkModelImplementation()

    def _validate_benchmark_model(self, benchmark_name):
        filename = 'models/' + benchmark_name + '.py'
        if os.path.isfile(filename):
            raw = Path(filename).read_text()
            if raw.find('class BenchmarkModelImplementation') == -1:
                raise ImportError('Cannot find class BenchmarkModelImplementation in '
                                  + filename)
            else:
                return self._load_benchmark_model(benchmark_name)
        else:
            raise ImportError('Cannot find plugin ' + filename)

    def main(self):
        try:
            self.model = self._validate_benchmark_model(self.args.name +
                                                        '_model')
        except ImportError as err:
            print(err)
            self.parser.print_help()

        print(self.model)
        self.model.run_benchmark(self.args.benchmark_options, "prout")

        identity = str(args.name + '_' + args.compiler + '_' + args.compiler_flags.replace(" ", "") +
               '_' + args.machine_type + '_' + args.benchmark_options.replace(" ", "") +
               '_' + args.build_number)
        execname = re.sub("[^a-zA-Z0-9_]+", "", identity).lower()
        report_name = identity + '.report'




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run some benchmark.')
    parser.add_argument('name', metavar='benchmark_name', type=str,
                    help='The name of the benchmark to be run')
    parser.add_argument('machine_type', type=str,
                    help='The type of the machine to run the benchmark on')
    parser.add_argument('compiler', type=str,
                    help='The compiler with which to compile the benchmark')
    parser.add_argument('--compiler-flags', type=str, default='',
                    help='The compiler flags to use with compiler')
    parser.add_argument('--benchmark-options', type=str, default='',
                    help='The benchmark options to use with the benchmark')
    parser.add_argument('--build-number', type=str, required=True,
                    help='The number of the benchmark run this is')
    args = parser.parse_args()

    controller = BenchmarkController(parser, args)
    controller.main()
