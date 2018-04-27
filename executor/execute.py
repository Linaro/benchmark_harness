"""
 Execute Commands, return out/err, accepts parser plugins

 Usage:
  out, err = Execute.run(['myapp', '-flag', 'etc'], outp=Plugin, errp=None)

 Plugin: parses the output of a specific benchmark, returns a dict()
         passing None makes run() returns plain text as str()
         use isinstance(out, dict) to differentiate handling
"""

import subprocess
import re

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

    def parse(self, output):
        """Parses the raw output, returns dictionary"""
        if not isinstance(output, str):
            raise TypeError("Output must be string")
        if not output:
            return dict()

        data = dict()
        for field, regex in self.fields.items():
            match = re.search(regex, output)
            if match:
                data[field] = self.sanitise(match.group(1))

        return data

def run(program, outp=None, errp=None):
    """Execute Commands, return out/err, accepts parser plugins"""
    # validate arguments
    if program and not isinstance(program, list):
        raise TypeError("Program needs to be a list of arguments")
    if outp and not isinstance(outp, OutputParser):
        raise TypeError("Output parser needs to derive from OutputParser")
    if errp and not isinstance(errp, OutputParser):
        raise TypeError("Error parser needs to derive from OutputParser")

    # Call the program
    result = subprocess.run(program,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    # Collect the results, parse if parser available
    if outp:
        stdout = outp.parse(result.stdout.decode('utf-8'))
    else:
        stdout = result.stdout.decode('utf-8')
    if errp:
        stderr = errp.parse(result.stderr.decode('utf-8'))
    else:
        stderr = result.stderr.decode('utf-8')

    # Return
    return stdout, stderr
