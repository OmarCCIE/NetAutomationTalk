#!/usr/bin/env python
#Author: Omar Lopez
#Twitter: https://twitter.com/OmarCCIE
#Github: https://github.com/OmarCCIE


from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from netaddr import *

device_list = {
    'R1' : {
        'ip' : '10.0.0.51',
        'rol' : 'R1'
    },
    'R2' : {
        'ip' : '10.0.0.52',
        'rol' : 'R2'
    },
    'SW1' : {
        'ip' : '10.0.0.53',
        'rol' : 'SW1'
    },
    'SW2' : {
        'ip' : '10.0.0.54',
        'rol' : 'SW2'
    },
    'SW3' : {
        'ip' : '10.0.0.55',
        'rol' : 'SW3'
    },
}

def configRouter(vlan,ip,rol):
    HSRP_IP = f'{ip.network.words[0]}.{ip.network.words[1]}.{ip.network.words[2]}.{int(ip.network.words[3]) + 1}'
    config_set = \
f'interface gigabitEthernet 0/1.{vlan} \n \
encapsulation dot1q {vlan} \n \
description VLAN{vlan} \n \
standby 10 ip {HSRP_IP} \n \
standby 10 preempt \n'

    #Define la IP a configurar en la interface
    if rol == 'R1':
        newIP = f'{ip.network.words[0]}.{ip.network.words[1]}.{ip.network.words[2]}.{int(ip.network.words[3]) + 2}'
        config_set = config_set + f' ip address {newIP} {ip.netmask} \n'
         #Si VLAN es Par, se agrega configuración de HSRP Activo
        if int(vlan) % 2 == 0:
            config_set = config_set + ' standby 10 priority 150 \n'

            
    elif rol == "R2":
        newIP = f'{ip.network.words[0]}.{ip.network.words[1]}.{ip.network.words[2]}.{int(ip.network.words[3]) + 3}'
        config_set = config_set + f' ip address {newIP} {ip.netmask} \n'
        #Si VLAN es ImPar, se agrega configuración de HSRP Activo
        if int(vlan) % 2 != 0:
            config_set = config_set + ' standby 10 priority 150 \n'

    config_set = config_set + '\n'

    return config_set

def configSwitchCore(vlan,subnet,rol):
    config_set = \
f'vlan {vlan} \n \
 name SUBNET_{subnet.network} \n \
! \n \
interface range GigabitEthernet0/0 - 2 \n \
 switchport trunk allow vlan add {vlan} \n \
! \n '

    if rol == "SW1":
        if int(vlan) % 2 == 0:
            config_set = config_set + f'spanning-tree vlan {vlan} priority 0 \n'
        else:
            config_set = config_set + f'spanning-tree vlan {vlan} priority 4096 \n'
    elif rol == "SW2":
        if int(vlan) % 2 != 0:
            config_set = config_set + f'spanning-tree vlan {vlan} priority 0 \n'
        else:
            config_set = config_set + f'spanning-tree vlan {vlan} priority 4096 \n'

    return config_set

def configSwitchAccess(vlan,subnet,interface,modo):
    config_set = \
f'vlan {vlan} \n \
 name SUBNET_{subnet.network} \n \
! \n \
interface range GigabitEthernet0/1 - 2 \n \
 switchport trunk allow vlan add {vlan} \n \
! \n '

    if modo == "access":
        config_set = config_set + \
f'interface GigabitEthernet{interface} \n \
 description To device subnet {subnet.network} \n \
 switchport mode access \n \
 switchport access vlan {vlan} \n \
!'
    elif modo == "trunk":
        config_set = config_set + \
f'interface GigabitEthernet{interface} \n \
 description To device subnet {subnet.network} \n \
 switchport trunk encapsulation dot1q \n \
 switchport mode trunk \n \
 switchport trunk allow vlan add {vlan} \n \
!'

    return config_set

def connectAndConfigure(device, managementIP, config):
    username = 'admin'
    password = 'Cisco!123'

    ios_device = {
        'device_type' : 'cisco_ios',
        'ip' : managementIP,
        'username' : username,
        'password' : password
    }
    print (f"Conectando a {device} en {managementIP}")
    try:
        net_connect = ConnectHandler(**ios_device)
    except (AuthenticationException):
        print ('Authentication Failure: ' + managementIP)
        
    except (NetMikoTimeoutException):
        print ('Timeout to device: ' + managementIP)
        
    except  (EOFError):
        print ('End of file while attempting device ' + managementIP)
        
    except (SSHException):
        print ('SSH Issue. Are you sure SSH is enabled? ' + managementIP)
        
    except Exception as unknown_error:
        print ('Some other error ' + unknown_error)
        

    output = net_connect.send_config_set(config)
    print(output)

def main():
    #Solicita datos a configurar a usuario
    vlanNumber = input ("Número de VLAN a configurar? ")
    subnet = input ("Subnet a configurar? (x.x.x.x/len, ej. 192.168.1.0/24: ")
    interfaceAccess = input ("Interface a configurar en Switch de access (x/y, Ej, 1/0: ")
    modoInterface = input ("En que modo se configurará (access,trunk): ")

    print (f'Se configurará la VLAN {vlanNumber} con la subred {subnet}')

    #Convierte a objecto IPNetwork subnet ingresada
    ip = IPNetwork(subnet)

    for device in device_list:
        getConfig = ""
        if device_list[device]['rol']  == 'R1' or device_list[device]['rol']  == 'R2':
            getConfig = configRouter(vlanNumber,ip,device_list[device]['rol'])


        if device_list[device]['rol']  == 'SW1' or device_list[device]['rol']  == 'SW2':
            getConfig = configSwitchCore(vlanNumber,ip,device_list[device]['rol'])
            

        if device_list[device]['rol']  == 'SW3':
            getConfig = configSwitchAccess(vlanNumber,ip,interfaceAccess, modoInterface)
            

        print (device + ':\n' + getConfig)

        connectAndConfigure(device, device_list[device]['ip'], getConfig.splitlines())


if __name__ == '__main__':
    main()

