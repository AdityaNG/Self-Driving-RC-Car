import os
import socket
from multiprocessing import Process

'''
prefs.py
This files handles:
    1. Setting prefs
    2. Getting prefs
    3. Dropping prefs
'''

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
    

def start_prefs_server():
    s = socket.socket()          
    print("Socket successfully created")
    
    # reserve a port on your computer in our 
    # case it is 12345 but it can be anything 
    port = 8083               
    
    # Next bind to the port 
    # we have not typed any ip in the ip field 
    # instead we have inputted an empty string 
    # this makes the server listen to requests  
    # coming from other computers on the network 
    s.bind(('', port))         
    print("socket binded to %s" %(port) )
    
    # put the socket into listening mode 
    s.listen(5)      
    print("socket is listening")  
    
    # a forever loop until we interrupt it or  
    # an error occurs 
    while True: 
        
        # Establish connection with client. 
        c, addr = s.accept()      
        print('Got connection from', addr)
        
        # send a thank you message to the client.  
        c.send(b'Thank you for connecting') 
        
        # Close the connection with the client 
        c.close() 

def prefs_server_online():
    pass

if not prefs_server_online():
    p = Process(target=start_prefs_server)
    p.start()