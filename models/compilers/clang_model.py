#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models.compilers.compiler_model import CompilerModel

class ModelImplementation(CompilerModel):
    def __init__(self):
        super().__init__()
        self.name='llvm'
        self.version=''
        self.frontend_name='clang'
        self.default_compiler_flags='-O3 -ffast-math -ffp-contract=on'
        self.default_dependencies=[]
