import os

'''
prefs.py
This files handles:
    1. Setting prefs
    2. Getting prefs
    3. Dropping prefs
'''

PAIRING_KEY = "PAIRING_KEY"

destfolder = "prefs/"
if not os.path.exists(destfolder):
    os.makedirs(destfolder)


def get_pref_time(p):
    stick_config = destfolder + p + ".txt"
    file_exists = os.path.isfile(stick_config) 

    if not file_exists:
        f=open(stick_config, "w")
        f.write("")
        f.close()

    f=open(stick_config, "r")

    if f.mode == 'r':
        return os.path.getmtime(stick_config)
    else:
        print("Permission Error : "+ stick_config)
        exit(1)

def get_pref(p):
    stick_config = destfolder + p + ".txt"
    file_exists = os.path.isfile(stick_config) 

    if not file_exists:
        f=open(stick_config, "w")
        f.write("")
        f.close()
        return ""

    f=open(stick_config, "r")

    if f.mode == 'r':
        return f.read()
    else:
        print("Permission Error : "+ stick_config)
        exit(1)

def set_pref(p, val):
    stick_config = destfolder + p + ".txt"
    f=open(stick_config, "w")
    f.write(str(val))
    f.close()

def drop_pref(p):
    stick_config = destfolder + p + ".txt"
    f=open(stick_config, "w")
    f.write("")
    f.close()
