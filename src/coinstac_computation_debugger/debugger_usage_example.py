#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script can be copied in your repository and  paste it in the folder
where lcoal and remote scripts exists; modify variables with TODO comments
and run/debug using this script
"""
import os
import warnings

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
from local import *
from remote import *
from computation_debugger import *


def new_debugger():
    TEST_DIR = "../test/test_data_dir_XXXX/" #TODO: replace with test dir path
    DEBUG_DIR = os.path.join(TEST_DIR, "DEBUG_new")
    temp_dir_prefix = "run1"


    NUM_CLIENTS = 2
    dbg= CoinstacComputationDebugger(NUM_CLIENTS, TEST_DIR, DEBUG_DIR)
    local_calls_list=[local_0, local_1, local_2] #TODO: replace with your local calls in order being executed
    remote_calls_list=[remote_0, remote_1, remote_2]#TODO: replace with your remote calls in order being executed
    num_iterations = len(local_calls_list)

    dbg.run_iterations(os.path.join(TEST_DIR, 'input', 'inputspec-eimhear-anthony.json'), num_iterations , local_calls_list ,remote_calls_list )


    print("Done processing...")

if __name__ == '__main__':
    new_debugger()

