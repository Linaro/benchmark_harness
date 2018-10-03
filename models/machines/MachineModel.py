#!/usr/bin/env python3

class MachineModel(object):
    def __init__(self):
        self.arch = ''
        self.num_cores = 1
        self.comp_flags=''
        self.link_flags=''

    def _machine_specific_setup(self):
        pass

    def get_flags(self):
        self._machine_specific_setup()
        return self.comp_flags, self.link_flags
