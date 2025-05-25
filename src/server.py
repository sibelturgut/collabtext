#this class represents the server side.
#in our application server is also a user, but the one who host the file
#server initiates and waits for new connections
#server user has the chance to select port and maybe other configurations if necessary 
#maybe we can add a security configuration (select ip addresses who can connect)

import threading #required for multiple connection

def start_server():
    pass

def connect(): #function to use in threads. threads will call this function for each connection and keep connected
    pass

def broadcast_changes():
    pass

def acquire_lock():
    pass

def release_lock():
    pass