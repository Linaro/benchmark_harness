#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Factory the instantiates and return the valid (dynamic) module/class
    from a machine names.
"""
from models.ModelFactory import ModelFactory
from executor.Execute import Execute

class MachineFactory(ModelFactory):
    """Identify and return the correct machine model"""

    def __init__(self, name):
        self.name = name
        if not name:
            self.name = self._auto_detect()
        super(MachineFactory, self).__init__('machines')

    def _auto_detect(self):
        """Detect architecture if empty"""

        result = Execute().run(['uname', '-m'])
        if result.returncode:
            msg = "'uname -m' error: [" + result.stderr + "]"
            raise RuntimeError("Error auto-detecting machine type: " + msg)
        if not result.stdout:
            raise RuntimeError("Unable to detect machine type with uname")
        return result.stdout.strip()

    def getMachine(self):
        """Loads machine model and returns"""

        return self._load_model(self.name + '_model.py')
