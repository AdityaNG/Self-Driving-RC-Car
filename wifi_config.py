import os
import subprocess

WIFI_CREDENTIALS = [('JioFi_207B1D0', 'q07abe03zn'), ('dobbyads', '9672345606')]

"""
@author adityang5@gmail.com

# To connect to a network : 
>>> single_network('dobbyads', '96723456061')
>>> restart_wifi()

# To check if connection succeeded : 
>>> is_connected()
True/False
"""

# Sets wpa_supplicant to the given network
# Works for hidden networks
def single_network(ssid, password):
    a = '''country=IN
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
ssid="''' + ssid + '''"
scan_ssid=1
key_mgmt=WPA-PSK
psk="''' + password + '''"
proto=RSN
key_mgmt=WPA-PSK
pairwise=CCMP TKIP
group=CCMP TKIP
auth_alg=OPEN
}
'''

    wpa_supplicant = '/etc/wpa_supplicant/wpa_supplicant.conf'

    f = open(wpa_supplicant,"w")
    f.write(a)


def restart_wifi():
    os.system('sudo ifdown --force wlan0; sudo ifup wlan0')


# TODO : Find a reliable way to check connection status
def is_connected():
    try:
        return "broadcast" in str(subprocess.run(['ifconfig'], stdout=subprocess.PIPE)).split('wlan0:')[1] 
    except:
        return False


# Use the below functions with caution (buggy)

def add_network(ssid, password):
    a = '''
network={
ssid="''' + ssid + '''"
scan_ssid=1
key_mgmt=WPA-PSK
psk="''' + password + '''"
proto=RSN
key_mgmt=WPA-PSK
pairwise=CCMP TKIP
group=CCMP TKIP
auth_alg=OPEN
}
'''

    wpa_supplicant = '/etc/wpa_supplicant/wpa_supplicant.conf'
    f = open(wpa_supplicant, 'r')
    data = f.read()
    if '"'+ssid+'"' not in data:
        # append
        f=open(wpa_supplicant, "a+")
        f.write(a)
    else:
        # edit
        lines = data.split('\n')
        res = lines
        for i in range(len(lines)):
            line = lines[i]
            if line == 'ssid="' + ssid + '"':
                res[i+3] = 'psk="' + password + '"'
                break
        
        f = open(wpa_supplicant,"w")
        f.write("\n".join(res))


def remove_network(ssid):
    wpa_supplicant = '/etc/wpa_supplicant/wpa_supplicant.conf'
    f = open(wpa_supplicant, 'r')
    data = f.read()
    if '"'+ssid+'"' not in data:
        # do nothing
        print("Network not in data")
    else:
        # edit
        lines = data.split('\n')
        start = 0
        end = 0
        
        flag = 0
        for i in range(len(lines)):
            line = lines[i]
            if line == "network={":
                start = i

            if flag == 1 and line == "}":
                end = i
                break

            if line == 'ssid="' + ssid + '"':
                flag = 1
        
        print("Range : ", (start, end))

        res = []
        for i in range(len(lines)):
            if not start<=i<=end:
                if lines[i]!='':
                    res.append(lines[i])
        #print("\n".join(res))
        f = open(wpa_supplicant,"w")
        f.write("\n".join(res))