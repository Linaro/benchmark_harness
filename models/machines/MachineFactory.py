#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Factory the instantiates and return the valid (dynamic) module/class
    from a machine names.
"""
from models.ModelFactory import ModelFactory

class MachineFactory(ModelFactory):
    """Identify and return the correct machine model"""
    # TODO: Identify machines via specific test (uname, etc)

    def __init__(self, name):
        self.name = name
        super(MachineFactory, self).__init__('machines')

    def getMachine(self):
        """Loads machine model and returns"""
        return self._load_model(self.name + '_model.py')
