#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import re
import shutil

class CompilerModel(object):

    def __init__(self):
        self.name = ''
        self.version = ''
        self.cxx_name = ''
        self.cc_name = ''
        self.fc_name = ''
        self.default_compiler_flags = ''
        self.default_link_flags = ''

    def _check_version(self, path):
        if not path:
            path = self.cc_name
        if not path:
            return ''
        if not os.path.isfile(path):
            path = shutil.which(path)
        if not os.path.isfile(path):
            return ''

        output = subprocess.check_output([path, '--version']).decode('utf-8')
        if self.cc_name in output:
            found = re.search(
                r'' + re.escape(self.cc_name) + r'.*? (\d*\.\d*\.\d*)', output)
            if found:
                self.version = found.group(1)
            self.cc_name = path
            return True
        else:
            return False

    def _check_binary(self, path):

        if not path or \
           not os.path.isfile(path) or \
           not os.access(path, os.X_OK):
            return False

        if self._check_version(path):
            self.compilers_path = os.path.realpath(os.path.dirname(path))
            self.sysroot_path = os.path.realpath(os.path.join(path, '../'))
            return True
        else:
            return False

    def check(self, bin_path):
        if os.path.isdir(bin_path):
            for file in os.listdir(bin_path):
                if file == self.cc_name:
                    return self._check_binary(os.path.join(bin_path, file))
            return False
        elif os.path.isfile(bin_path):
            return self._check_binary(bin_path)
        else:
            return False

    def get_env(self):
        return {
            'cxx': os.path.join(self.compilers_path, self.cxx_name),
            'cc': os.path.join(self.compilers_path, self.cc_name),
            'fc': os.path.join(self.compilers_path, self.fc_name),
            'lib': os.path.realpath(os.path.join(self.compilers_path, '../lib'))
        }

    def get_flags(self):
        return self.default_compiler_flags, self.default_link_flags
