#! /usr/bin/env python3

from DNA_ATH import dnac
import json
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from prettytable import PrettyTable





# Silence the insecure warning due to SSL Certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def dnac_login(host, username, password):
    url = "https://{}/api/system/v1/auth/token".format(dnac['host'])
    token = requests.request("POST", url, auth=HTTPBasicAuth(username, password),
                                verify=False)
    data = token.json()
    return data['Token']



def network_device(dnac, token):

    response = requests.request("GET", "https://{}/dna/intent/api/v1/network-device?errorCode=SERIAL-NUMBER-CONFLICT".format(dnac['host']), 
 
        headers={
            'X-Auth-Token': '{}'.format(token),
            'Content-type': 'application/json'
        },
        verify=False
    )

    data = response.json()
    
    for x in range(0,25):
    #print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))
        print(data["response"][x]["managementIpAddress"] +'   '+data["response"][x]["errorDescription"]+ '\n\n' )




login = dnac_login(dnac["host"], dnac["username"], dnac["password"])
network_device(dnac, login)

#print(dnac_devices)
