#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Factory the instantiates and return the valid (dynamic) module/class
    from a benchmark.
"""

from models.ModelFactory import ModelFactory

class BenchmarkFactory(ModelFactory):
    """Find and return a benchmark model"""

    def __init__(self, name):
        self.name = name
        super(BenchmarkFactory, self).__init__('benchmarks')

    def getBenchmark(self):
        """Loads benchmark model and returns"""
        return self._load_model(self.name + '_model.py')
