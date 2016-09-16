import sys
import requests
import time
from logger import Logger

requests.packages.urllib3.disable_warnings()

class Import(object):
    """
    Import modules (LTM, Firewall, APM, AFM, ASM)
    """
    logger = Logger.create_logger(__name__)
    def __init__(self, config=None):
        self.config = config


    def import_ltm(self, config, devid):
        """
        Import LTM
        """
        iq = self.config['bigiq']
        ip = config['bigip']
        username = config['username']
        password = config['password']
        root_username = config['root_username']
        root_password = config['root_password']

        self.logger.info("Import BIGIP {0} in LTM".format(ip))

        uri= 'https://' + iq + '/mgmt/cm/adc-core/tasks/declare-mgmt-authority'
        link = '/cm/system/machineid-resolver/{0}'.format(devid)
        device_json = {'deviceReference': {'link': link}, 'uuid': devid, 'deviceUri': 'http://' + ip + ':443', 'machineId': devid}

        result=0
        response = requests.post(uri, str(device_json), auth=(username, password), verify=False)
        json_str = response.json()

        uri=json_str['selfLink'].replace('localhost', iq)
        i=0
        while True:
            response = requests.get(uri, auth=(username, password), verify=False)
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
                self.logger.info("Status LTM Import = {0} expecting FINISHED. {1}".format(json_str['status'], i))

        if result==1:
            return True
        else:
            return False


    def import_sec(self, config, devid, afm=False, asm=False, apm=False):
        """
        Import AFM, ASM, APM
        """
        iq = self.config['bigiq']
        ip = config['bigip']
        username = config['username']
        password = config['password']
        root_username = config['root_username']
        root_password = config['root_password']


	if afm==True:
            self.logger.info("Import BIGIP {0} in AFM".format(ip))
            uri= 'https://' + iq + '/mgmt/cm/firewall/tasks/declare-mgmt-authority'
            link = 'https://' + ip + '/mgmt/shared/resolver/device-groups/cm-firewall-allFirewallDevices/devices/{0}'.format(devid)
            device_json = {"deviceIp": ip, "deviceReference": {"link": link}, "snapshotWorkingConfig": 'false', "reimport": 'false', "useBigiqSync": 'false', "skipDiscovery": 'true', "validationBypassMode": "BYPASS_FINAL", "username": "admin", "createChildTasks": 'true', "name": 'import-firewall'}
 	
	result=0
        response = requests.post(uri, str(device_json), auth=(username, password), verify=False)
        json_str = response.json()

        uri=json_str['selfLink'].replace('localhost', iq)
        i=0
        while True:
            response = requests.get(uri, auth=(username, password), verify=False)
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
                self.logger.info("Status AFM Import = {0} expecting FINISHED. {1}".format(json_str['status'], i))

        if result==1:
            return True
        else:
            return False

