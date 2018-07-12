#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import importlib
import importlib.util
from pathlib import Path


class ModelLoader(object):
    def __init__(self, path):
        self.path = path
        self._check_model()

    def load(self):
        """Class loader python style"""
        model_name = re.sub("[*.py]", "", os.path.basename(self.path))
        spec = importlib.util.spec_from_file_location(model_name, self.path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.ModelImplementation()

    def _check_model(self):
        """Verifies that the file actually contains the model class"""
        if not os.path.isfile(self.path):
            raise ImportError('Bad Path ' + self.path)

        raw = Path(self.path).read_text()
        if raw.find('class ModelImplementation') == -1:
            raise ImportError('Model %s does not implement ModelImplementation' %
                              self.path)
