#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models.compilers.CompilerModel import CompilerModel

class ModelImplementation(CompilerModel):
    def __init__(self):
        super().__init__()
        self.name = 'gcc'
        self.version=''
        self.cxx_name='g++'
        self.cc_name='gcc'
        self.fortran_name='gfortran'
        self.default_compiler_flags='-O3 -ffast-math -funroll-loops'
        self.default_dependencies=[]

