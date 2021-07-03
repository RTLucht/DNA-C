from MY_ATH import ERS
import requests
import json
import urllib3
import base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



IP = input('What is the IP of the devices ')
Name = IP.replace(".",'_')
host = ERS['ise_node']
user =  ERS['ers_user']
password = ERS['ers_pass']


url = "https://"+host+":9060/ers/config/networkdevice"
creds = str.encode(':'.join((user, password)))
encodedAuth = bytes.decode(base64.b64encode(creds))



payload = json.dumps({
  "NetworkDevice": {
    "name": "NAD_"+ Name,
    "description": "",
    "authenticationSettings": {
      "networkProtocol": "RADIUS",
      "radiusSharedSecret": "Key"
    },
    "tacacsSettings": {
      "sharedSecret": "Key",
      "connectModeOptions": "OFF"
    },
    "NetworkDeviceIPList": [
      {
        "ipaddress": IP,
        "mask": 32
      }
    ],
    "NetworkDeviceGroupList": [
      "Agency#",
      "Device Type#",
      "Location#",
      "class#c"
    ]
  }
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'authorization': " ".join(("Basic",encodedAuth)),
}

response = requests.request("POST", url, headers=headers, data=payload, verify=False)

print(response.text)
