#!/usr/bin/env python3
from models.machines.MachineModel import MachineModel

class ModelImplementation(MachineModel):
    def __init__(self):
        super().__init__()
        self.arch = 'aarch64'

    def _detect_name(self):
        """Auto-detect name, based on CPU parameters"""

        if 'Model name' in self.cpu_info:
            return self.cpu_info['Model name']

        #       CPUs   C/S  Nodes Sockets
        # D03    16     4     1     4 (likely to change in the future)
        # D05    64    32     4     2
        # Amber 46-92  46     1    1-2
        # Tx2  28~224  28     2    1-2
        elif int(self.cpu_info['CPU(s)']) == 16 and \
             int(self.cpu_info['Socket(s)']) == 4:
            return "D03"

        elif int(self.cpu_info['CPU(s)']) == 64 and \
             int(self.cpu_info['Socket(s)']) == 2 and \
             int(self.cpu_info['NUMA node(s)']) == 4:
            return "D05"

        elif int(self.cpu_info['Core(s) per socket']) == 46 and \
             int(self.cpu_info['NUMA node(s)']) == 1:
            return "Amberwing"

        elif int(self.cpu_info['Core(s) per socket']) == 28 and \
             int(self.cpu_info['NUMA node(s)']) == 2:
            return "ThunderX2"
