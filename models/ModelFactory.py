#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Base Factory class, with common logic for finding and loading models
"""
import os
import re
import importlib
from models.ModelLoader import ModelLoader

class ModelFactory(object):
    """Identify and return the correct machine model"""

    def __init__(self, model_type):
        if model_type is None:
            raise ValueError('Model type is empty')
        if not isinstance(model_type, str):
            raise TypeError('Model type has to be a string')

        self.root = os.path.dirname(os.path.realpath(__file__))
        self.model_type = model_type
        self.models_dir = os.path.join(self.root, self.model_type)

    def _load_model(self, name):
        if name is None:
            raise ValueError('Model name is empty')
        if not isinstance(name, str):
            raise TypeError('Model name has to be a string')
        if not re.search('_model.py', name):
            return None

        filename = os.path.join(self.models_dir, name)
        if not os.path.isfile(filename):
            return None

        return ModelLoader(filename).load()

    def _find_model(self, condition):
        """Checks compiler models against binary dir"""

        for model in [f for f in os.listdir(self.models_dir)
                        if re.match(r'.*\.py*', f)]:
            loaded_model = self._load_model(model)
            if loaded_model and loaded_model.check(condition):
                return loaded_model

        # If did not find module that satisfies the conditions, bail
        raise ImportError('No corresponding module found for %s' %
                          self.model_type)
