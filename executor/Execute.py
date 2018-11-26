#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 Execute Commands, return out/err, accepts parser plugins

 Usage:
  out, err = Execute(outp=Plugin, errp=None).run(['myapp', '-flag', 'etc'])

 Plugin: parses the output of a specific benchmark, returns a dict()
         passing None makes run() returns plain text as str()
         use isinstance(out, dict) to differentiate handling
"""

import subprocess
import re

from helper.BenchmarkLogger import BenchmarkLogger

class OutputParser:
    """Base class for all output (out/err) parsers that will be passed
       to the Execute class."""
    def __init__(self):
        # Interesting fields in output, with regex to match
        self.fields = None
        # Filters to clean up matched output using replace
        self.filters = {
            # commas can appear in middle of numbers, depending on locale
            ',' : ''
        }

    def sanitise(self, string):
        """Sanitise using cleanup rules"""
        for find, repl in self.filters.items():
            string = string.replace(find, repl)
        return string

    def parse(self, cmdline, output):
        """Parses the raw output, returns dictionary"""
        if not isinstance(output, str):
            raise TypeError("Output must be string")
        if not output:
            return dict()

        data = {
            '_name': self._get_name(cmdline)
        }
        for field, regex in self.fields.items():
            match = re.search(regex, output)
            if match:
                data[field] = self.sanitise(match.group(1))
        return data

    def _get_name(self, cmdline):
        """Extracts name from cmdline, taking into consideration perf/taskset"""
        if not isinstance(cmdline, list):
            raise TypeError("command line needs to be a list")
        index = 0
        if cmdline[index].endswith('taskset'):
            index += 2
        if cmdline[index].endswith('perf'):
            index += 2
        name = re.search(r'\/([^\/]+)$', cmdline[index])
        if name:
            return name.group(1)
        return ''

class Execute(object):
    """Executes commands, captures output, parse with plugins"""

    def __init__(self, outp=None, errp=None, logger=None):
        # validate arguments
        if outp and not isinstance(outp, OutputParser):
            raise TypeError("Output parser needs to derive from OutputParser")
        if errp and not isinstance(errp, OutputParser):
            raise TypeError("Error parser needs to derive from OutputParser")

        self.outp = outp
        self.errp = errp
        self.logger = logger

    def run(self, program):
        """Execute Commands, return out/err, accepts parser plugins"""

        if program and not isinstance(program, list):
            raise TypeError("Program needs to be a list of arguments")
        if not program:
            raise ValueError("Need program arguments to execute")

        if self.logger:
            self.logger.debug('Executing: %s' % repr(program))

        # Call the program, capturing stdout/stderr
        result = subprocess.run(program,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
 
        # Collect stdout, parse if parser available
        stdout = result.stdout.decode('utf-8')
        if self.outp:
            stdout = self.outp.parse(program, stdout)
        result.stdout = stdout

        # Collect stderr, parse if parser available
        stderr = result.stderr.decode('utf-8')
        if self.errp:
            stderr = self.errp.parse(program, stderr)
        result.stderr = stderr
 
        # Return
        return result
