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
import subprocess
from urllib.request import urlretrieve
from helper.cd import cd
from models.ModelFactory import ModelFactory
from shutil import which

class CompilerFactory(ModelFactory):
    """Fetch, prepare and setup compilers"""

    def __init__(self, toolchain_url, toolchain_extractpath):
        self.toolchain_url = toolchain_url
        self.toolchain_extractpath = toolchain_extractpath
        super(CompilerFactory, self).__init__('compilers')

    def getCompiler(self):
        """Gets a compiler from URL or system local"""

        if re.match("(http|ftp)://", self.toolchain_url):
            # URLs that we can use urlretrieve
            self.filename = self.toolchain_url.split('/')[-1]
            self.dirname = re.sub("\.(tar|tgz)\.?(gz|xz)?", "", self.filename)
            self.base = os.path.join(self.toolchain_extractpath, self.dirname)
            self.path = os.path.join(self.toolchain_extractpath, self.filename)
            extracted_tar = self._download_toolchain()
            return self._fetch_compiler(extracted_tar)
        elif re.match("file://", self.toolchain_url):
            # full path, just remove "file://"
            return self._fetch_system(self.toolchain_url[7:])
        elif re.search("://", self.toolchain_url):
            raise ValueError('URL not supported: %s' % self.toolchain_url)
        else:
            # Assume this is either a path or a toolchain name
            return self._fetch_system(self.toolchain_url)

    def _extract_tarball(self, filename):
        """Extracts toolchain directory"""

        tarball = tarfile.open(filename)
        tarball.extractall(self.toolchain_extractpath)

        # TODO: self.toolchain_extractpath and self.base are disconnected
        if not os.path.isdir(self.base):
            raise ImportError('Toolchain directory name %s does not match' %
                              self.base)

    def _download_toolchain(self):
        """Downloads toolchain tarball"""
        filename, headers = urlretrieve(self.toolchain_url, self.path)

        if not os.path.isfile(filename):
            raise ImportError('Error downloading toolchain to %s' % filename)

        return self._extract_tarball(filename)

    def _fetch_compiler(self, extracted_tar):
        """Fetches the full path to the frontend executable"""

        for root, dirs, _ in os.walk(self.base):
            if 'bin' in dirs:
                return self._find_model(os.path.join(root, 'bin'))
        raise ImportError('Compiler binary dir not found')

    def _fetch_system(self, compiler):
        """Identifies the system toolchain's full path"""

        compiler_path = which(compiler)
        if compiler_path is None:
            raise ImportError('Compiler %s not installed' % compiler)

        return self._find_model(compiler_path)
