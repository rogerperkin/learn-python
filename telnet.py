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