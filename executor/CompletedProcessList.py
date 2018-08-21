#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import CompletedProcess
import yaml

class CompletedProcessList:
    """ Simple list of CompletedSubprocess to collate out, err, return codes """
    def __init__(self):
        self.returncode = 0
        self.list = []
        self.idx = 0

    def append(self, result):
        """ Adds a new CompleteProcess to the list"""
        if not isinstance(result, CompletedProcess):
            raise TypeError("result must be a CompleteProcess")
        self.list.append(result)
        self.returncode += result.returncode

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx >= len(self.list):
            self.idx = 0
            raise StopIteration
        self.idx += 1
        return self.list[self.idx-1]

    def __getitem__(self, idx):
        self.idx = 0
        return self.list[idx]

    def stdout(self):
        out = ''
        if not self.list:
            return out
        if isinstance(self.list[0].stdout, dict):
            outs = []
            for r in self.list:
                if r.stdout:
                    outs.append(r.stdout)
            out = yaml.dump(outs, default_flow_style=False)
        else:
            for r in self.list:
                if r.stdout:
                    out += r.stdout
        return out

    def stderr(self):
        err = ''
        if not self.list:
            return err
        if isinstance(self.list[0].stderr, dict):
            errs = []
            for r in self.list:
                if r.stderr:
                    errs.append(r.stderr)
            err = yaml.dump(errs, default_flow_style=False)
        else:
            for r in self.list:
                if r.stderr:
                    err += r.stderr
        return err
