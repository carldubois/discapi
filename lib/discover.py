import sys
import requests
import time
from logger import Logger

requests.packages.urllib3.disable_warnings()

try:
    import json as json_out 
except ImportError:
    import simplejson as json_out

class Discover(object):
    """
    Trust and Discover BIGIP
    """
    logger = Logger.create_logger(__name__)
    def __init__(self, config=None):
        self.config = config

    def device_trust(self, config):
        """
	Trust # BIGIP
    	"""
	iq = self.config['bigiq']
        ip = config['bigip']
        username = config['username']
        password = config['password']
        root_username = config['root_username']
        root_password = config['root_password']

	self.logger.info("Create a device-trust for BIGIP {0} in ADC".format(ip))
	uri = 'https://' + iq + '/mgmt/cm/global/tasks/device-trust'
	device_json = {'address': ip, 'userName': username, 'password': password, 'clusterName': '', 'useBigiqSync': 'false'}
	response = requests.post(uri, data=str(device_json), auth=(username, password), verify=False)
        response = requests.get(uri, auth=(username, password), verify=False)
	
	# dump json trust task
	json_str = response.json()

        for item in json_str['items']: 
           if item['address'] == ip:
               uri=item['selfLink'].replace('localhost', iq)
               
               i=0
               while True:
                   response = requests.get(uri, auth=(username, password), verify=False)
                   json_str = response.json()
                   if json_str['currentStep'] == 'PENDING_FRAMEWORK_UPGRADE_CONFIRMATION':
                       #patch the device-trust task
                       trust_json = {'confirmFrameworkUpgrade':'true'} 
                       requests.patch(uri, trust_json, auth=(username, password), verify=False)
                   elif json_str['status'] == 'FINISHED':
                       result=1
                       break
                   elif json_str['status'] == 'FAILED':
                       result=0
                       break
                   else:
                       time.sleep(1)
                       i+=1
                       self.logger.info("Device Trust Status = {0} expecting FINISHED. {1}".format(item['status'], i))

        # get device reference and return
        response = requests.get(uri, auth=(username, password), verify=False)
	json_str = response.json()

        if result==1:
            return True, json_str['machineId']
        else:
            return False, '1fb0ab85-0dd6-413c-a374-6ca24bf5a44e' 


    def ltm_discover(self, config, devid):
	"""
        Discover BIGIP in Device / ADC
       	"""
        iq = self.config['bigiq']
        ip = config['bigip']
        username = config['username']
        password = config['password']
        root_username = config['root_username']
        root_password = config['root_password']
	self.logger.info("Discover BIGIP {0} in Device".format(ip))

        uri= 'https://' + iq + '/mgmt/cm/global/tasks/device-discovery'
        link = 'cm/system/machineid-resolver/{0}'.format(devid)

        device_json = {'deviceReference': {"link": link}, 'moduleList': [{'module': 'adc_core'},{'module': 'firewall'},{'module': 'security_shared'}], 'userName': username, 'password': password, 'rootUser': root_username, 'rootPassword': root_password, 'automaticallyUpdateFramework' : 'true'}

        result=0
        response = requests.post(uri, data=str(device_json), auth=(username, password), verify=False)
	json_str = response.json()

        uri=json_str['selfLink'].replace('localhost', iq)
        i=0
        while True:
            response = requests.get(uri, auth=(config['username'], config['password']), verify=False)
	    json_str = response.json()

            if json_str['status'] == 'FINISHED':
                result=1
                break
            elif json_str['status'] == 'FAILED':
                result=0
                break
            else:
                time.sleep(1)
                i+=1
                self.logger.info("Discovery Status = {0} expecting FINISHED. {1}".format(json_str['status'], i))


        if result==1:
            return True
        else:
            return False

