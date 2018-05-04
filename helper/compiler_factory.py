#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Factory the instantiates and return the valid (dynamic) module/class
    from a toolchain_url or frontend binary name installed locally.

    It takes the toolchain_url/name and path to extract it (or not) from the
    caller. Then you call getCompiler() on it.

    Note that at the moment it is up to the factory to determine wether it is a
    toolchain to be downloaded or something already installed systemwide.
    It could be adapted to take a path to a toolchain.
"""
import tarfile
import os
import re
import importlib
from urllib.request import urlretrieve
from pathlib import Path
from helper.cd import cd
from helper.model_loader import ModelLoader
from shutil import which


class CompilerFactory(object):
    """The Wonderful Factory of Compilers"""

    def __init__(self, toolchain_url, toolchain_extractpath):
        self.toolchain_url = toolchain_url
        self.toolchain_extractpath = toolchain_extractpath

    def getCompiler(self):
        """This is the method that will discriminate between downloading and
        calling locally installed toolchain"""
        if self.toolchain_url.find('http') != -1 or self.toolchain_url.find('ftp') != -1:
            extracted_tar = self._downloadToolchain()
            return self._fetchCompiler(extracted_tar)
        else:
            return self._fetch_system(self.toolchain_url)

    def _fetch_system(self, compiler):
        """Fetch a locally installed toolchain registered with the shell"""
        compiler_path = which(compiler)
        if compiler_path is not None:
            return self._getCompilerFromBinaries(compiler_path)
        else:
            raise ImportError('Compiler %s not installed' % compiler)

    def _downloadToolchain(self):
        """Downloads... toolchain !"""
        with cd(self.toolchain_extractpath):
            filename, headers = urlretrieve(self.toolchain_url)
            before = os.listdir()
            # We need to find out what the extracted dir is called
            tarball = tarfile.open(filename)
            tarball.extractall()
            after = os.listdir()
            filename = [x for x in after if x not in before]
            # Substract the before list of directories to the after list
            return filename[0]

    def _fetchCompiler(self, extracted_tar):
        """Fetches the full path to the frontend executable"""
        original_path = os.getcwd()
        with cd(self.toolchain_extractpath):
            with cd(extracted_tar):
                for root, dirnames, _ in os.walk('.'):
                    for dirname in dirnames:
                        if dirname == 'bin':
                            # Yes this is ugly
                            with cd(original_path):
                                return self._getCompilerFromBinaries(
                                    os.path.join(self.toolchain_extractpath,
                                                 extracted_tar, dirname))
        raise ImportError('Frontend not found...')

    def _getCompilerFromBinaries(self, bin_path):
        """Loads each model class and calls it to check if the frontend is
        theirs"""
        original_path = os.getcwd()
        list_compiler_modules = [f for f in os.listdir('./models/compilers/')
                                 if re.match(r'.*\.py*', f)]
        for model in list_compiler_modules:
            if model.find('_model') != -1:
                try:
                    loaded_model = ModelLoader(model, 'compiler', original_path).load()
                    if loaded_model.check(bin_path):
                        return loaded_model
                except ImportError as err:
                    pass
        raise ImportError('No corresponding module found for toolchain @ ' +
                          self.toolchain_url)
