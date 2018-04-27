#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This helper class is designed to work well with the 'with' directive of
    Python. As long as you are in the indented block, your current working dir
    is changed to one you cd'd to. When you leave the block, you exit. (no pun
    intended)

    This comes straight from StackOverflow
"""
import os

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
