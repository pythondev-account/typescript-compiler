import ipaddress
import json
import os
import re
import subprocess
from helper import read_file, execute_command, validate_input, get_interfaces, validate_ipv4_address, validate_ipv4_network
from interface import set_static_ip, fix_all_interface
from strings import Strings

    
def parse_dhcp(json_data):
    subnet4 = json_data.get("Dhcp4", {}).get("subnet4", [])
    dhcp = []
    for subnet in subnet4:
        interface = subnet.get("interface")
        subnet_cidr = subnet.get("subnet")
        dhcp.append(DHCP(interface, subnet_cidr, exsiting_config=subnet))
    return dhcp

def process_reservation(reservation_str):
    mac_regex = r'^([0-9a-fA-F]{2}[:]){5}[0-9a-fA-F]{2}$'
    mac_addr = reservation_str.split(' ')[0]
    ip_addr = reservation_str.split(' ')[1]
    if not re.match(mac_regex, mac_addr):
        try:
            mac_addr = ':'.join(['{:02x}'.format((int(mac_addr) >> ele) & 0xff) for ele in range(0,48,8)][::-1])
        except ValueError:
            print(f"Invalid MAC address: {mac_addr}")
            return
    if not validate_ipv4_address(ip_addr):
        print(f"Invalid IP address: {ip_addr}")
        return
    return (mac_addr, ip_addr)

def process_adding_entry():
    interface = validate_input(f"Enter interface name: ({' '.join(get_interfaces())}):\n> ", lambda x: x in get_interfaces() and x != "lo")
    subnet = validate_input(Strings.DHCP.input_subnet, validate_ipv4_network)
    reservations = []
    complete_reservations = False
    print(Strings.DHCP.input_reservation)
    while not complete_reservations:
        reservation = validate_input("> ", lambda x: x.lower() == '' or len(x.split(' ')) == 2)
        if reservation.lower() == '':
            complete_reservations = True
        else:
            reservation_entry = process_reservation(reservation)
            if reservation_entry:
                reservations.append(reservation_entry)
    dhcp_entry = DHCP(interface, subnet, reservations)
    return dhcp_entry

class DHCP:
    def __init__(self, interface, subnet, reservations=None, exsiting_config=None):
        self.interface = interface
        self.subnet = ipaddress.ip_network(subnet, strict=False)
        self.reservations = reservations if reservations is not None else []
        self.exsiting_config = exsiting_config

    def __repr__(self):
        return f"DHCP(interface={self.interface}, subnet={self.subnet}, reservations={self.reservations}, exsiting_config={bool(self.exsiting_config)})"
    
    @property
    def gateway(self):
        hosts = list(self.subnet.hosts())
        return str(hosts[0])
    
    @property
    def netmask(self):
        return str(self.subnet.prefixlen)
    
    @property
    def pool_start(self):
        hosts = list(self.subnet.hosts())
        return str(hosts[1])

    @property
    def pool_end(self):
        hosts = list(self.subnet.hosts())
        return str(hosts[-1])
    
    def subnet4(self):
        if self.exsiting_config:
            return self.exsiting_config
        else:
            return {
            "subnet": str(self.subnet),
            "interface": self.interface,
            "pools": [
                {
                    "pool": f"{self.pool_start}-{self.pool_end}"
                }
            ],
            "reservations": [
                {
                    "hw-address": hw,
                    "ip-address": ip
                } for hw, ip in self.reservations
            ],
            "option-data": [
                {
                    "name": "routers",
                    "data": self.gateway
                },
                {
                    "name": "domain-name-servers",
                    "data": "8.8.8.8"
                }
            ]
        }

def generate_config(dhcp_list):
    subnet4 = []
    for i, dhcp in enumerate(dhcp_list, start=1):
        subnet4.append({
            "id": i,
            **dhcp.subnet4()
        })
    kea_config = {
        "Dhcp4": {
            "interfaces-config": {
                "interfaces": [dhcp.interface for dhcp in dhcp_list]
            },
            "subnet4": subnet4
        }
    }
    return kea_config

def save_config_to_file(config):
    with open('/etc/kea/kea-dhcp4.conf', 'w') as f:
        json.dump(config, f, indent=4)
    execute_command('kea-dhcp4 -t /etc/kea/kea-dhcp4.conf')

def main():
    dhcp = []
    try:
        kea_config = read_file('/etc/kea/kea-dhcp4.conf')
        kea_json = json.loads(kea_config)
        dhcp = parse_dhcp(kea_json)
    except Exception as e:
        print(f"{Strings.DHCP.dhcp_json_failure}. Error detail: {e}")
    print("Current DHCP Configuration:\n")
    print(dhcp)
    print(Strings.DHCP.main_help)
    not_done = True
    while not_done:
        dhcp_input = validate_input(Strings.DHCP.main_input, lambda x: x in ['a', 'n', 'm', 'p'])
        if dhcp_input == 'a':
            new_entry = process_adding_entry()
            dhcp.append(new_entry)
            print(dhcp)
        elif dhcp_input == 'n':
            dhcp.clear()
            print(dhcp)
        elif dhcp_input == 'm':
            print("Saving DHCP configuration and reloading DHCP server...")
            save_config_to_file(generate_config(dhcp))
            static_ip = validate_input("Do you want to set a static IP for the DHCP server interface? (y/n): ", lambda x: x.lower() in ['y', 'n'])
            if static_ip.lower() == 'y':
                for entry in dhcp:
                    fix_all_interface()
                    set_static_ip(entry.interface, f"{entry.gateway}/{entry.netmask}")
            execute_command('systemctl restart kea-dhcp4.service')
            not_done = False
        elif dhcp_input == 'p':
            print(generate_config(dhcp))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting DHCP configuration. Nothing is changed!")