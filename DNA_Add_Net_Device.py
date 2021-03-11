from DNA_ATH import dnac
import json
import requests
import urllib3
import sys
from requests.auth import HTTPBasicAuth



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


device_ip = input('Enter IP address: ')
 

def dnac_login(host, username, password):
    url = "https://{}/api/system/v1/auth/token".format(dnac['host'])
    token = requests.request("POST", url, auth=HTTPBasicAuth(username, password),
                                verify=False)
    data = token.json()
    return data['Token']



def add_device(dnac, token):
    
    device_object = {
        'ipAddress': [
            device_ip
        ],
        'type': 'NETWORK_DEVICE',
        'computeDevice': 'False',
        'snmpVersion': 'v2',
        'snmpROCommunity': dnac["SNMPRO"],
        'snmpRetry': '3',
        'snmpTimeout': '5',
        'cliTransport': 'SSH',
        'userName': dnac["username"],
        'password': dnac["password"]
    }
    response = requests.request("POST", 'https://{}/dna/intent/api/v1/network-device'.format(dnac['host']), 
        data=json.dumps(device_object),
        headers={
            'X-Auth-Token': '{}'.format(token),
            'Content-type': 'application/json'
        },
        verify=False
    )
    #print(response.text.encode('utf8'))
    return response.json()

login = dnac_login(dnac["host"], dnac["username"], dnac["password"])
add_device(dnac, login)
