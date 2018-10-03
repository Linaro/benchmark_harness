#!/usr/bin/env python3
from models.machines.MachineModel import MachineModel

class ModelImplementation(MachineModel):
    def __init__(self):
        super().__init__()
        self.arch = 'x86_64'

    def _detect_name(self):
        """Auto-detect name, based on CPU parameters"""

        # x86_64 usually have good cpuinfo, so "Model name" is fine
        if 'Model name' in self.cpu_info:
            return self.cpu_info['Model name']
        # If specific cases arise, implement below
        return ''
