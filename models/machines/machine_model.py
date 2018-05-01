#!/usr/bin/env python3

class MachineModel(object):
    def __init__(self):
        self.mbench_flags=''
        self.mcomp_flags=''
        self.mlink_flags=''

    def _machine_specific_setup(self):
        pass

    def main(self):
        self._machine_specific_setup()
        return self.mcomp_flags, self.mlink_flags
