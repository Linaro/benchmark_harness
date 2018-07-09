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
import subprocess
from urllib.request import urlretrieve
from pathlib import Path
from helper.cd import cd
from helper.model_loader import ModelLoader
from shutil import which


class CompilerFactory(object):
    """The Wonderful Factory of Compilers"""

    def __init__(self, toolchain_url, sftp_user, toolchain_extractpath):
        self.toolchain_url = toolchain_url
        self.sftp_user = sftp_user
        self.toolchain_extractpath = toolchain_extractpath

    def getCompiler(self):
        """Gets a compiler from URL or system local"""
        # TODO: Make this smarter, to account for:
        #        * Local binary name (find sysroot)
        #        * Local directory name (find sysroot, binaries)
        #        * Local tarball (unpack, find sysroot, binaries)
        #        * file:// URL, same as above
        #        * Better URL check

        if 'sftp' in self.toolchain_url:
            # TODO: This doesn't belong here
            extracted_tar = self.__sftp_toolchain()
            return self._fetch_compiler(extracted_tar)
        elif '://' in self.toolchain_url:
            # TODO: Assuming HTTP/FTP for now
            self.filename = self.toolchain_url.split('/')[-1]
            self.dirname = re.sub("\.(tar|tgz)\.?(gz|xz)?", "", self.filename)
            self.base = os.path.join(self.toolchain_extractpath, self.dirname)
            self.path = os.path.join(self.toolchain_extractpath, self.filename)
            extracted_tar = self._download_toolchain()
            return self._fetch_compiler(extracted_tar)
        else:
            return self._fetch_system(self.toolchain_url)

    def __sftp_toolchain(self):
        """Fetches the Toolchain via sftp"""

        # TODO: This doesn't belong here
        if len(self.toolchain_url.split('/')) < 4:
            raise EnvironmentError('SFTP URL is not valid %s' %
                                   self.toolchain_url)

        sftp_ip = self.toolchain_url.split("/")[2:3][0]
        sftp_filepath = '/'.join(self.toolchain_url.split("/")[3:])
        sftp_filename = self.toolchain_url.split('/')[-1]

        if self.sftp_user != '':
            sftp_user = self.sftp_user + '@'
        else:
            sftp_user = ''

        with cd(self.toolchain_extractpath):
            stdout = subprocess.check_output(['sftp -o ForwardAgent=yes -o ConnectTimeout=60 -o \
                                              UserKnownHostsFile=/dev/null -o \
                                              StrictHostKeyChecking=no ' +
                                              sftp_user + sftp_ip +
                                              ':/' + sftp_filepath],
                                             stderr=subprocess.STDOUT, shell=True)
            return self._extract_tarball(sftp_filename)

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

    def _find_model(self, bin_path):
        """Checks compiler models against binary dir"""

        # TODO: Lift this to Model Loader
        original_path = os.getcwd()
        list_compiler_modules = [f for f in os.listdir('./models/compilers/')
                                 if re.match(r'.*\.py*', f)]
        for model in list_compiler_modules:
            if model.find('_model') != -1:
                try:
                    loaded_model = ModelLoader(
                        model, 'compiler', original_path).load()
                    if loaded_model.check(bin_path):
                        return loaded_model
                except ImportError as err:
                    # TODO: Fix this with a proper check in Model Loader
                    pass
        raise ImportError('No corresponding module found for toolchain @ ' +
                          self.toolchain_url)
