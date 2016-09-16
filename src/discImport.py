#!/usr/bin/env python
# -*- coding: utf-8 -*-

#@Author: Carl Dubois
#@Email: c.dubois@f5.com
#@Description: Discover / Import BIGIP
#@Product: BIGIQ
#@VersionIntroduced: 5.0.0

"""
trust, discover, import ltm, asm, afm
"""

import sys
import argparse
from discover import Discover
from import_modules import Import
from time import strftime
from logger import Logger

def wf_dma(LOGGER, disc, imp, config, args):
    
    result = [] 

    #==========================
    # Trust
    #==========================
    result_trust = disc.device_trust(config)
    result.append(result_trust)
  
    #==========================
    # Discover
    #==========================
    if result_trust[0] == False:
	LOGGER.error('Trust failed or device already under management')
	sys.exit(1)
    else:
        result_disc  = disc.ltm_discover(config, result_trust[1])   
    	result.append(result_disc)
    #==========================
    # Import LTM
    #==========================
    result_ltm = imp.import_ltm(config, result_trust[1])
    if result_ltm == False:
        LOGGER.error('Discover LTM failed.')
        sys.exit(1)
    else:
	result.append(result_ltm)
	
    #==========================
    # Import AFM, ASM, APM
    #==========================
    
    result_sec = []

    if args.afm==1:
    	result_afm = imp.import_sec(config, result_trust[1], afm=True)
    	result_sec.append(result_afm)
    # ASM not working
    if args.asm==1:
    	result_asm = imp.import_sec(config, result_trust[1], asm=True)
    	result_sec.append(result_asm)
    # APM not working
    if args.apm==1:
    	result_apm = imp.import_sec(config, result_trust[1], apm=True)
    	result_sec.append(result_apm)
    # All modules disabled.
    if args.afm == args.asm == args.apm == 0:
	LOGGER.info('No security modules imported.')
 
    result.append(result_sec)  	
    return result

if __name__ == '__main__':
    #==========================
    # Logger
    #==========================
    LOGGER = Logger.create_logger(__name__)

    #==========================
    # Help
    #==========================
    parser = argparse.ArgumentParser(description='Workflow Trust, Discover, Import LTM, AFM, ASM.')
    parser.add_argument('--config', type=str, help='Configuration,IQ-IP address, user, pass.')
    parser.add_argument('--afm', type=int, help='Import AFM')
    parser.add_argument('--asm', type=int, help='Import ASM')
    parser.add_argument('--apm', type=int, help='Import APM')


    args = parser.parse_args()

    #==========================
    # Read config file
    #==========================
    file = args.config
    config={}

    if file:
    	file = '../../../config/{0}'.format(file)
	with open (file) as infile:
	    print infile
	    for line in infile:
               (key, val) = line.split(' = ')
               config[str(key)] = val.strip('\n')
    else:
	LOGGER.error("No configuration file.")
	sys.exit(1)

    #==========================
    # Trust, Discover
    #==========================
    Discover = Discover(config)
    Import = Import(config)
    result = wf_dma(LOGGER, Discover, Import, config, args) 
    if result[0][0] == True: LOGGER.info('Device Trust - PASS.')
    if result[1] == True:    LOGGER.info('Device Discovery - PASS.')
    if result[2] == True:    LOGGER.info('ADC Import - PASS.')
    if result[3][0] == True: LOGGER.info('AFM Import - PASS.')
