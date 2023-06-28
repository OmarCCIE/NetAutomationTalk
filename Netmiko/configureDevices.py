#!/usr/bin/env python

from netmiko import ConnectHandler
from paramiko.ssh_exception import SSHException


with open('Netmiko/commands_file') as f:
    commands_to_send = f.read().splitlines()

with open('Netmiko/device_list') as f:
    devices_list = f.read().splitlines()

for devices in devices_list:
    ip_address_of_device = "omarlc.ddns.net"
    print ('Connecting to device ' + devices)
    port = devices
    ios_device = {
        'device_type' : 'cisco_ios',
        'ip' : ip_address_of_device,
        'port' : port,
        'username' : "admin",
        'password' : "Cisco!123"
    }

    try:
        net_connect = ConnectHandler(**ios_device)
    except  (EOFError):
        print ('End of file while attempting device ' + ip_address_of_device)
        continue
    except (SSHException):
        print ('SSH Issue. Are you sure SSH is enabled? ' + ip_address_of_device)
        continue
    except Exception as unknown_error:
        print ('Some other error ' + unknown_error)
        continue

    
    output = net_connect.send_config_set(commands_to_send)
    print(output)
    net_connect.disconnect() 