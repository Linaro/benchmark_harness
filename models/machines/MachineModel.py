#!/usr/bin/env python3

import re
from executor.Execute import Execute

class MachineModel(object):
    def __init__(self):
        self.arch = ''
        self.name = ''
        self.num_cores = 1
        self.comp_flags=''
        self.link_flags=''
        self.cpu_info = None
        self.affinity = []
        self._get_cpu_info()
        self._get_mem_info()
        self._get_cpu_affinity()
        if not self.name or self.name == self.cpu_info['Architecture']:
            self.name = self._detect_name()
        if not self.num_cores and 'threads' in self.cpu_info:
            machine.num_cores = self.cpu_info['threads']

    def _get_cpu_info(self):
        """Auto detects hardware configuration (cores, cache, etc)"""

        if not self.cpu_info or not isinstance(self.cpu_info, dict):
            self.cpu_info = dict()

        # Top-up self.cpu_info about CPU and architecture (json output is not common)
        for source in ['lscpu'], ['cat', '/proc/cpuinfo']:
            values = Execute().run(source)
            for line in values.stdout.split('\n'):
                if not line:
                    continue
                key, value = re.split('\s*:\s*', line)
                self.cpu_info[key] = value.strip()

        # Update self.cpu_info structre with standard args (in addition to lscpu)
        self.cpu_info['threads'] = int(self.cpu_info['CPU(s)'])
        self.cpu_info['core_span'] = int(self.cpu_info['Thread(s) per core'])
        self.cpu_info['node_span'] = int(self.cpu_info['threads'] / int(self.cpu_info['NUMA node(s)']))
        self.cpu_info['socket_span'] = int(self.cpu_info['threads'] / int(self.cpu_info['Socket(s)']))

        # Cache mapping
        core_values = Execute().run(['lscpu', '-e'])
        cores = core_values.stdout.split('\n')
        fields = re.split("\s+", cores[0])

        # Cache self.cpu_info is optional, assume linear otherwise
        # Format: L1d:L1i:L2:L3
        if 'L1d' in fields[4]:
            l2_span = 0
            l3_span = 0
            # First line is header, last is empty
            for core in cores[1:-1]:
                cache_fields = re.split("\s+", core)[4].split(':')
                l2 = int(cache_fields[2])
                l3 = int(cache_fields[3])
                if not l2:
                    l2_span = l2_span + 1
                if not l3:
                    l3_span = l3_span + 1
                if l2 and l3:
                    break
            self.cpu_info['l2_span'] = l2_span
            self.cpu_info['l3_span'] = l3_span
        else:
            self.cpu_info['l2_span'] = self.cpu_info['threads']
            self.cpu_info['l3_span'] = self.cpu_info['threads']

    def _get_mem_info(self):
        """Auto detects memory configuration"""

        if not self.cpu_info or not isinstance(self.cpu_info, dict):
            self.cpu_info = dict()

        # Top-up self.cpu_info about memory
        values = Execute().run(['free', '-g'])
        for line in values.stdout.split('\n'):
            # Format: "Mem|Swap: <total> ..."
            match = re.match("^(\w+):\s+(\d+)\s", line)
            if match:
                self.cpu_info[match.group(1)] = match.group(2)

    # Basic assumptions:
    #  - Core count starts at 1 (taskset does)
    #  - First core is always noisy, so pick +1 for every metric
    #  - 'core' identifies hyper-threads on intel, not Arm
    #  - A zero in the array means lower quality boundaries
    def _get_cpu_affinity(self):
        """Selects affinity of cores into a priority list"""

        if not self.cpu_info or not isinstance(self.cpu_info, dict):
            raise RuntimeError("Can't check affinity without cpu info")

        if 'threads' not in self.cpu_info or self.cpu_info['threads'] <= 1:
            return [0]

        has_core = 'core_span' in self.cpu_info
        has_node = 'node_span' in self.cpu_info
        has_socket = 'socket_span' in self.cpu_info
        has_l2 = 'l2_span' in self.cpu_info
        has_l3 = 'l3_span' in self.cpu_info

        # Identical groups can be collapsed
        if has_core and has_node and self.cpu_info['core_span'] == self.cpu_info['node_span']:
            self.cpu_info.pop('core_span')
        if has_socket and has_node and self.cpu_info['socket_span'] == self.cpu_info['node_span']:
            self.cpu_info.pop('node_span')
        if has_l3 and has_l2 and self.cpu_info['l3_span'] == self.cpu_info['l2_span']:
            self.cpu_info.pop('l2_span')

        # Prioritise socket, NUMA, HT
        todo = list(range(1,self.cpu_info['threads']+1))
        self.affinity = []
        for group in 'socket_span', 'node_span', 'l3_span', 'l2_span', 'core_span':
            if not group in self.cpu_info:
                continue
            if self.cpu_info['threads'] != self.cpu_info[group]:
                if self.cpu_info[group] == 1:
                    self.affinity.append(0)
                core = 2
                while core <= self.cpu_info['threads']:
                    if core in todo:
                        self.affinity.append(core)
                        todo.remove(core)
                    core += self.cpu_info[group]

        # Lastly, fill up the missing ones linearly (zero means worst quality)
        self.affinity.append(0)
        self.affinity.extend(todo)

    def get_flags(self):
        self._machine_specific_setup()
        return self.comp_flags, self.link_flags
