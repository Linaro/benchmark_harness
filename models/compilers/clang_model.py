#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models.compilers.CompilerModel import CompilerModel

class ModelImplementation(CompilerModel):
    def __init__(self):
        super().__init__()
        self.name = 'clang'
        self.version=''
        self.cc_name='clang'
        self.cxx_name='clang++'
        self.fc_name='flang'
        self.default_compiler_flags='-O3 -ffast-math -ffp-contract=on'
