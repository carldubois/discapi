import sys
import requests
import time
from logger import Logger
import json

requests.packages.urllib3.disable_warnings()

try:
    import json as json_out 
except ImportError:
    import simplejson as json_out

class Virtuals(object):
    """
    List and Manage Virtual Serers
    """
    logger = Logger.create_logger(__name__)
    def __init__(self, config=None):
        self.config = config

    def create_virtual(self, config):
    	"""
	List all virtual servers
    	"""
	iq = config['bigiq']
        ip = config['bigip']
        username = config['ip_username']
        password = config['ip_password']
        iq_username = config['iq_username']
        iq_password = config['iq_password']

 	self.logger.info("Get machine id for a BIGIP {0} in ADC and create a virutal".format(ip))
    	uri = 'https://' + iq + '/mgmt/cm/system/machineid-resolver?filter=address eq' + ip
	response = requests.get(uri, auth=(iq_username, iq_password), verify=False)

	# dump json trust task
	json_str = response.json()
    	result = []

        for item in json_str['items']: 
           if item['address'] == ip:
                device = item['machineId']

                # Create a node
                uri = 'https://' + iq + '/mgmt/cm/adc-core/working-config/ltm/node'
                node_json = {"partition": "Common", "name": "node1", "address": "10.128.20.13", "deviceReference": {"link": "https://localhost/mgmt/shared/resolver/device-groups/cm-adccore-allbigipDevices/devices/" + str(item['machineId'])}}
                node = requests.post(uri, data=str(node_json), auth=(iq_username, iq_password), verify=False)
                print "Create node"
                result.append(node.status_code)

                # Create a pool
                uri = 'https://' + iq + '/mgmt/cm/adc-core/working-config/ltm/pool'
                pool_json = {"partition": "Common", "name": "pool1", "loadBalancingMode": "round-robin", "deviceReference": {"link": "https://localhost/mgmt/shared/resolver/device-groups/cm-adccore-allbigipDevices/devices/" + str(item['machineId'])}}
                pool = requests.post(uri, data=str(pool_json), auth=(iq_username, iq_password), verify=False)
                print "Create pool"
                result.append(pool.status_code)

                # Add a pool member (node) to a pool
                uri = 'https://' + iq + '/mgmt/cm/adc-core/working-config/ltm/pool/' + pool.json()['id'] + '/members'
                members_json = {"partition": "Common", "name": "node1:80", "port": 80, "nodeReference": {"link": "https://localhost/mgmt/cm/adc-core/working-config/ltm/node/" + str(node.json()['id'])}}
                members = requests.post(uri, data=str(members_json), auth=(iq_username, iq_password), verify=False)
                print "Add pool member (node) to a pool"
                result.append(members.status_code)

                # Create a virtual server
                uri = 'https://' + iq + '/mgmt/cm/adc-core/working-config/ltm/virtual/'
                virtual_json = {"partition": "Common", "name": "virtual1", "destinationAddress": "10.128.10.114", "mask": "255.255.255.255", "destinationPort": 80, "sourceAddress": "0.0.0.0/0", "deviceReference": {"link": "https://localhost/mgmt/shared/resolver/device-groups/cm-adccore-allbigipDevices/devices/" + str(item['machineId'])}}
                virtuals = requests.post(uri, data=str(virtual_json), auth=(iq_username, iq_password), verify=False)
                print "Create a virtual server"
                result.append(virtuals.status_code)

                uri = 'https://' + iq + '/mgmt/cm/adc-core/working-config/ltm/virtual/' + virtuals.json()['id']
                pool_ref_json = {"poolReference": {"link": "https://localhost/mgmt/cm/adc-core/working-config/ltm/pool/" + str(pool.json()['id'])}}
                pool_reference = requests.patch(uri, data=str(pool_ref_json), auth=(iq_username, iq_password), verify=False)

                result.append(pool_reference.status_code)

                # Attach profiles to a virtual server
                uri = 'https://' + iq + '/mgmt/cm/adc-core/working-config/ltm/profile/ipother'
                profile = requests.get(uri, auth=(iq_username, iq_password), verify=False)
                print "Attach profile to a virtual server"
                result.append(profile.status_code)

                for item in profile.json()['items']:
                    if item['name'] == 'ipother':
                        uri = 'https://' + iq + '/mgmt/cm/adc-core/working-config/ltm/virtual/' + virtuals.json()['id'] + '/profiles'
                        profile_json = {"name": "ipother", "partition": "Common", "profileIpotherReference": {"link": str(item['selfLink'])}, "context": "all"}
                        virtual_profile = requests.post(uri, data=str(profile_json), auth=(iq_username, iq_password), verify=False)
                
                i=0
                size=len(result)
                while i <= size:
                    if result[i-1] == 200:
                        i+=1
                    else:
                        return False
                return True