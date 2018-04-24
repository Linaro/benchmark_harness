#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models.compilers.compiler_model import CompilerModel

class CompilerModelImplementation(CompilerModel):
    def __init__(self):
        super().__init__()
        self.name='g++'
        self.version='6.3.0'
        self.frontend_name='g++'
        self.default_compiler_flags='-O3 -ffast-math -ffp-contract=on'
        self.default_dependencies=[]
