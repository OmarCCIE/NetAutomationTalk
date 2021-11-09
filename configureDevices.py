#!/usr/bin/env python

from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
import logging

logging.basicConfig(filename='netmiko_global.log', level=logging.DEBUG)
logger = logging.getLogger("netmiko")

with open('commands_file') as f:
    commands_to_send = f.read().splitlines()

with open('device_list') as f:
    devices_list = f.read().splitlines()

for devices in devices_list:
    print ('Connecting to device ' + devices)
    ip_address_of_device = devices
    ios_device = {
        'device_type' : 'cisco_ios',
        'ip' : ip_address_of_device,
        'username' : "admin",
        'password' : "Cisco!123"
    }

    try:
        net_connect = ConnectHandler(**ios_device)
    except (AuthenticationException):
        print ('Authentication Failure: ' + ip_address_of_device)
        continue
    except (NetMikoTimeoutException):
        print ('Timeout to device: ' + ip_address_of_device)
        continue
    except  (EOFError):
        print ('End of file while attempting device ' + ip_address_of_device)
        continue
    except (SSHException):
        print ('SSH Issue. Are you sure SSH is enabled? ' + ip_address_of_device)
        continue
    except Exception as unknown_error:
        print ('Some other error ' + unknown_error)
        continue

    
    #output = net_connect.send_config_set(commands_to_send)
    #print(output)
    print (commands_to_send)
    net_connect.disconnect() 