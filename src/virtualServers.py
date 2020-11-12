#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
list, manage virtuals
"""
import os.path
import sys
sys.path += [os.path.abspath('../lib')]

import argparse
from virtual_server import Virtuals
from time import strftime
from logger import Logger

def cr_vs(LOGGER, virtual, config, args):    
    #result = []
    #==========================
    # Create virtual
    #==========================
    result_create = virtual.create_virtual(config)
    return result_create

def ls_vs(LOGGER, virtual, config, args):
    #==========================
    # List virtual
    #==========================
    result_list = virtual.list_virtual(config)
    return result_list 

if __name__ == '__main__':
    #==========================
    # Logger
    #==========================
    LOGGER = Logger.create_logger(__name__)

    #==========================
    # Help
    #==========================
    parser = argparse.ArgumentParser(description='Create and List Virtual Servers')
    parser.add_argument('--config', type=str, help='Configuration,IQ-IP address, user, pass.')
    parser.add_argument('--op', type=str, help='Create or List Virtual')

    args = parser.parse_args()
    #==========================
    # Read config file
    #==========================
    file = args.config
    op = args.op
    
    config={}

    if file:
    	file = '../config/{0}'.format(file)
	with open (file) as infile:
	    print infile
	    for line in infile:
               (key, val) = line.split(' = ')
               config[str(key)] = val.strip('\n')
    else:
	LOGGER.error("No configuration file.")
	sys.exit(1)

    #=============================
    # Create Virtuals and Operations
    #=============================
    Virtual = Virtuals()
    
    if op == "create":
        result = cr_vs(LOGGER, Virtual, config, args)
    elif op == "list":
        result = ls_vs(LOGGER, Virtual, config, args)

    if result == True: LOGGER.info('Create Application - PASS.')
