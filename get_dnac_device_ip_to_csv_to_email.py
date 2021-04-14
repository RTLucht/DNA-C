from DNA_ATH import dnac
import json
import requests
import urllib3
import sys
import re
import csv
import os
from requests.auth import HTTPBasicAuth
from mac_vendor_lookup import MacLookup
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib



host = dnac["host"]
username = dnac["username"]
password = dnac["password"]
name = input('Name of report: ')


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def macaddress():
    Token = dnac_login(host, username, password)

    with open('H:\Scripts\DNA\macs.txt') as f:
        macs = f.read().splitlines()
        
        for mac in macs:
            mac = mac.replace('.','')
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
            #print (mac,' IP of Device ',data['detail']['hostIpV4'],' Switch Name ',data['detail']['clientConnection'],' port ',data['detail']['port'])
            print (mac,data['topology']['nodes'][0]['ip'],(MacLookup().lookup(mac)),'Switch',data['detail']['clientConnection'],'Switch IP',data['topology']['nodes'][1]['ip'],'Port',data['detail']['port'])
        except KeyError:
            print (mac,'No Data')

 
        filename = 'H:/Scripts/DNA/' + name +'.csv'
        write_header = not os.path.exists(filename)
        with open(filename, 'a') as csvfile:
            headers = ['MAC Address', 'IP Address', 'OUI','Device Name','Switch IP','Port ID']
            writer = csv.DictWriter(csvfile,fieldnames=headers)
            if write_header:
                writer.writeheader()
            writer = csv.writer(csvfile)
            try:
                csvdata = (mac,data['topology']['nodes'][0]['ip'],(MacLookup().lookup(mac)),data['detail']['clientConnection'],data['topology']['nodes'][1]['ip'],data['detail']['port'])
            except KeyError:
                csvdata = (mac,'No Data')
            writer.writerow(csvdata)

        




        #filename = 'H:/Scripts/DNA/' + name +'.csv'
        #write_header = not os.path.exists(filename)
        #with open(filename, 'a') as csvfile:
        #    headers = ['MAC Address', 'IP Address', 'Switch name', 'Port']
        #    writer = csv.DictWriter(csvfile,fieldnames=headers)
        #    if write_header:
        #        writer.writeheader()
        #    writer = csv.writer(csvfile)
        #    csvdata = (mac, data['detail']['hostIpV4'], data['detail']['clientConnection'], data['detail']['port'])
        #    writer.writerow(csvdata)


if __name__ == "__main__":
    macaddress()

#print(dnac_devices)
#print(json.dumps(output, indent=2))




me = 'something@something.com'
server = 'mailserver:25'
you = 'something1@something.com'

text = """
Hello, Julie.

Here is your data: 


{table}

Regards,

AUTOM8"""

html = """


<html>
<head>
<style> 
  table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
  th, td {{ padding: 5px; }}
</style>
</head>

<body><p>Hello, Julie.</p>

<p>Here is your data for:</p>
<h1>"""+str(name)+"""</h1>
{table}
<p>Regards,</p>
<p>Me</p>
</body></html>
"""

with open('H:/Scripts/DNA/' + name +'.csv') as input_file:
    reader = csv.reader(input_file)
    data = list(reader)

text = text.format(table=tabulate(data, headers="firstrow", tablefmt="grid"))
html = html.format(table=tabulate(data, headers="firstrow", tablefmt="html"))

message = MIMEMultipart(
    "alternative", None, [MIMEText(text), MIMEText(html,'html')])

message['Subject'] = "Your data"
message['From'] = me
message['To'] = you
server = smtplib.SMTP(server)
server.ehlo()
server.starttls()
server.sendmail(me, you, message.as_string())
server.quit()