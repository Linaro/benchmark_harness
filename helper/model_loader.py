#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import importlib
from helper.cd import cd
from pathlib import Path


class ModelLoader(object):
    def __init__(self, model_name, class_type, root_path):
        self.model_name = model_name
        self.root_path = root_path
        self.class_type = class_type
        self.model_path = os.path.join(root_path, 'models/' + class_type + 's/'
                                       + model_name)

    def load(self):
        return self._load_model()

    def _validate_compiler_model(self):
        """Verifies that the file actually contains the model class"""
        if os.path.isfile(self.model_path):
            raw = Path(self.model_path).read_text()
            if raw.find('class ModelImplementation') == -1:
                return False
            else:
                return True
        else:
            raise ImportError('Bad Path ' + self.model_path)

    def _load_model(self):
        """Class loader python style"""
        if self._validate_compiler_model():
            with cd(self.root_path):
                self.model_name = re.sub("[*.py]", "", self.model_name)
                mod = importlib.import_module(
                    'models.' + self.class_type + 's.' + self.model_name)
            return mod.ModelImplementation()
        raise ImportError('Could not load %s model at %s' % (self.model_name,
                                                                 self.model_path))
