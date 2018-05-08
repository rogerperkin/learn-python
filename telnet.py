# Simple Python code that will telnet to the router defined in HOST
# Username and Pwd will be prompted for 
# Once connected the command show ip int brief will be run and output 

import getpass
import telnetlib

HOST = "192.168.106.50"
user = input("Username: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until(b"Username: ")
tn.write(user.encode('ascii') + b"\n")
if password:
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")

        tn.write(b"sh ip int brief | ex unass\n")
        tn.write(b"exit\n")
        print(tn.read_all().decode('ascii'))