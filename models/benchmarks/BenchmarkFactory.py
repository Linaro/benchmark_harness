#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Factory the instantiates and return the valid (dynamic) module/class
    from a benchmark.
"""
import os

from models.ModelFactory import ModelFactory

class BenchmarkFactory(ModelFactory):
    """Find and return a benchmark model"""

    def __init__(self, name, root_path):
        self.name = name
        self.extractpath = os.path.join(root_path, 'benchmark')
        super(BenchmarkFactory, self).__init__('benchmarks')

    def getBenchmark(self):
        """Loads benchmark model and returns"""
        model = self._load_model(self.name + '_model.py')
        if not model:
            raise ImportError("Can't find model for benchmark " + self.name)
        model.root_path = self.extractpath
        return model
