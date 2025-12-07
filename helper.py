import subprocess
import os
import ipaddress

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()
    
def execute_command(command):
    print(f"Executing command: {command}")
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Command '{command}' failed with error: {result.stderr}")
    return result.stdout.strip()

def validate_input(prompt, input_matcher=lambda *args: None):
    input_value = input(prompt)
    try:
        while not input_matcher(input_value):
            print("Invalid input, please try again.")
            input_value = input(prompt)
    except KeyboardInterrupt:
        print("\nInput cancelled by user.")
        exit(1)
    return input_value

def get_interfaces():
    return os.listdir('/sys/class/net/')

def display_interfaces():
    interfaces = get_interfaces()
    print("Available network interfaces:")
    for idx, iface in enumerate(interfaces, start=1):
        print(f"{idx}. {iface}")

def validate_ipv4_network(ip_str):
    try:
        ipnetwork = ipaddress.IPv4Network(ip_str, strict=False)
        if ipnetwork.prefixlen < 32:
            return True
        return False
    except (ipaddress.AddressValueError, ValueError):
        return False
    
def validate_ipv4_address(ip_str):
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except ipaddress.AddressValueError:
        return False