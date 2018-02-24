import socket
import time
import os

port = int(os.environ["DB_PORT"])
host = os.environ["DB_HOST"]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try: # to connect to the database
        s.connect((host, port))
        s.close()
        print("Successfully connected to db!")
        break
    except socket.error as ex:
        print ("waiting for db...")
        time.sleep(0.5) # handle and wait again
