#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script includes the local computations for linear mixed effects model
with decentralized statistic calculation
"""
import os
import warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
from local import *
from remote import *
from coinstac_computation_debugger import *


def new_debugger():
    TEST_DIR = "../test/eimhear-anthony-data/"
    DEBUG_DIR = os.path.join(TEST_DIR, "DEBUG_new")
    temp_dir_prefix = "run1"

    num_iterations = 3

    NUM_CLIENTS = 2
    dbg= CoinstacComputationDebugger(NUM_CLIENTS, TEST_DIR, DEBUG_DIR)
    local_calls_list=[local_0, local_1, local_2]
    remote_calls_list=[remote_0, remote_1, remote_2]
    dbg.run_iterations(os.path.join(TEST_DIR, 'input', 'inputspec-eimhear-anthony.json'), num_iterations , local_calls_list ,remote_calls_list )


    print("Done processing...")

if __name__ == '__main__':
    #old_debugger()
    new_debugger()

