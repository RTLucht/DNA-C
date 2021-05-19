
# Not a very clean script, I probalby have more things in here that I need
# I use this during monitoring stage of Network Access Control with Cisco ISE
# The idea is that anything hitting the default rule I would run a report
# that is a lot of lines since I reauth the default rule ever so often to keep them 
# on the report.  This Script here takes the Calling Station ID or the MAC addresses
# filters out duplicates then runs them against or Cisco DNA-C for IP address if known.
# I also do an OUI lookup on the MAC.  Then that file is sent to a SFTP for the particular 
# policy set in ISE. Now the this one runs every morning so for good messure I added a notification
# to be sent to a Webex Bot in a Room that I made for this.  If I don't get the message I know something
# is up.

#Enjoy


from DNA_ATH import dnac
from MY_ATH import SR_WEBEX
from MY_ATH import NDOTSFTP
import json
import requests
import urllib3
import sys
import re
import csv
import os
import pysftp
from requests.auth import HTTPBasicAuth
from mac_vendor_lookup import MacLookup
from tabulate import tabulate
import smtplib
import glob
import pandas as pd
from csv import DictReader
import time


host = dnac["host"]
username = dnac["username"]
password = dnac["password"]
named_tuple = time.localtime() # get struct_time
time_string = time.strftime("%m-%d-%Y,%H.%M", named_tuple)
time_string2 = time.strftime("%m-%d-%Y, %H:%M:%S", named_tuple)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def macaddress():
    Token = dnac_login(host, username, password)


    for names in glob.glob('*Whatever_file_name*.csv'):
                
        data = pd.read_csv(names)
        Dup_Rows = data[data.duplicated()]
        BF_RM_DUP = data.drop_duplicates(subset= "'CALLING_STATION_ID'", keep='first')        
            
        for mac in BF_RM_DUP["'CALLING_STATION_ID'"]:

            mac = mac.replace('.','')
            mac = mac.replace("'",'')
            mac = mac.replace(':','')
            mac = mac.replace('-','')
            mac = ''.join(mac.split())
            mac = ":".join(["%s" % (mac[i:i+2]) for i in range(0, 12, 2)])
            #reformat macs
            headers = {
                        'content-type': "application/json",
                        'x-auth-token': "",
                    }
            network_device_list(host,Token,headers,mac)






def dnac_login(host, username, password):
    url = "https://{}/api/system/v1/auth/token".format(host)
    response = requests.request("POST", url, auth=HTTPBasicAuth(username, password),
                                 verify=False)
    return response.json()["Token"]


def network_device_list(host, token, headers, mac):
        url = "https://"+ host +"/dna/intent/api/v1/client-detail?timestamp&macAddress=" + mac
        headers["x-auth-token"] = token
        response = requests.get(url, headers=headers, verify=False)
        #print(response)
        data = response.json()
        #print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))
        #print(json.dumps(data['topology']['nodes'], sort_keys=True, indent=4, separators=(',', ':')))

        try:
                        print (mac, data['topology']['nodes'][0]['ip'],(MacLookup().lookup(mac)))
        except KeyError:
            print (mac,' No Data')


        filename = 'H:/CSV_ISE_Stuff/NDOT_IP.csv'
        write_header = not os.path.exists(filename)
        with open(filename, 'a', newline='') as csvfile:
            headers = ['MAC Address', 'IP Address', 'OUI']
            writer = csv.DictWriter(csvfile,fieldnames=headers)
            if write_header:
                writer.writeheader()
            writer = csv.writer(csvfile)
            try:
                csvdata = (mac, data['topology']['nodes'][0]['ip'],(MacLookup().lookup(mac)))
            except KeyError:
                csvdata = (mac,' No Data')
            
            writer.writerow(csvdata)





if __name__ == "__main__":
    macaddress()

#print(dnac_devices)
#print(json.dumps(output, indent=2))


cnopts = pysftp.CnOpts()
cnopts.hostkeys = None   
with pysftp.Connection(host=NDOTSFTP["host"], username=NDOTSFTP["username"],
    password=NDOTSFTP["password"], cnopts=cnopts) as sftp:

    sftp.put('Whatever_2'+ time_string +'.csv')

    sftp.close

os.remove('Whatever_2.csv')


for files in glob.glob('*Whatever_file_name*.csv'):
    os.remove(files)




url = "https://webexapis.com/v1/messages?"

payload = json.dumps({
  "roomId": SR_WEBEX["ROOM"],
  "markdown": "NDOT Script Ran " +  time_string2
})
headers = {
  'Authorization': SR_WEBEX["BOT"],
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

#print(response.text)
