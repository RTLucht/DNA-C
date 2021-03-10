

from DNA_ATH import dnac
import json
import requests
import urllib3
import sys
from requests.auth import HTTPBasicAuth



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
mac = input('Enter mac address: ')
mac = mac.replace('','')
mac = mac.replace('.','')
mac = mac.replace(':','')
mac = mac.replace('-','')
mac = ''.join(mac.split())
mac = ":".join(["%s" % (mac[i:i+2]) for i in range(0, 12, 2)])
headers = {
            'content-type': "application/json",
            'x-auth-token': "",
            'entity_type': 'mac_address',
            'entity_value': mac,
        }


def dnac_login(host, username, password):
    url = "https://{}/api/system/v1/auth/token".format(host)
    response = requests.request("POST", url, auth=HTTPBasicAuth(username, password),
                                headers=headers, verify=False)
    return response.json()["Token"]


def network_device_list(dnac, token):
    url = "https://{}/dna/intent/api/v1/client-enrichment-details".format(dnac['host'])
    headers["x-auth-token"] = token
    response = requests.get(url, headers=headers, verify=False)
    #print(response)
    data = response.json()
    #print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))
    for item in data:
        try:
            print('The device ' + mac +' is on ' + item["userDetails"]["clientConnection"] + ' with management IP ' + item["connectedDevice"][0]["deviceDetails"]["managementIpAddress"] + ' port '+ item["userDetails"]["port"]+' with IP ' + item["userDetails"]["hostIpV4"])
        except:
            print(mac + json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))





login = dnac_login(dnac["host"], dnac["username"], dnac["password"])
network_device_list(dnac, login)

#print(dnac_devices)
#print(json.dumps(output, indent=2))