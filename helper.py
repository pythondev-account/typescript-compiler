import subprocess
import os
import ipaddress
import logging
import shlex

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def execute_command(command, check=True, timeout=30, suppress_errors=False):
    """
    Execute a shell command with robust error checking.
    
    Args:
        command (str): The command to execute
        check (bool): If True, raise exception on non-zero return code
        timeout (int): Command timeout in seconds (default: 30)
        suppress_errors (bool): If True, don't raise exceptions on errors
        
    Returns:
        str: Command output (stdout)
        
    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout
        Exception: If command fails and check=True and suppress_errors=False
    """
    # Validate command is not empty
    if not command or not command.strip():
        raise ValueError("Command cannot be empty")
    
    print(f"Executing command: {command}")
    
    try:
        # Run command with timeout
        result = subprocess.run(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            universal_newlines=True,
            timeout=timeout
        )
        
        # Check for errors
        if check and result.returncode != 0:
            error_msg = f"Command failed with return code {result.returncode}\n"
            error_msg += f"Command: {command}\n"
            if result.stderr:
                error_msg += f"Error output: {result.stderr}"
            if result.stdout:
                error_msg += f"\nStandard output: {result.stdout}"
            
            if not suppress_errors:
                raise Exception(error_msg)
            else:
                print(f"Warning: {error_msg}")
        
        return result.stdout.strip()
        
    except subprocess.TimeoutExpired as e:
        error_msg = f"Command timed out after {timeout} seconds: {command}"
        if not suppress_errors:
            raise Exception(error_msg) from e
        else:
            print(f"Warning: {error_msg}")
            return ""
    except Exception as e:
        if not suppress_errors:
            raise
        else:
            print(f"Warning: Command execution failed: {e}")
            return ""

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

def get_routes(interface=None):
    """
    Get current routing table entries.
    
    Args:
        interface (str): Optional interface name to filter routes
        
    Returns:
        str: Routing table output
    """
    try:
        if interface:
            cmd = f"ip route show dev {interface}"
        else:
            cmd = "ip route show"
        return execute_command(cmd, check=False, suppress_errors=True)
    except Exception as e:
        print(f"Failed to retrieve routes: {e}")
        return ""

def validate_route(destination, gateway):
    """
    Validate a route configuration.
    
    Args:
        destination (str): Destination network in CIDR notation
        gateway (str): Gateway IP address
        
    Returns:
        bool: True if valid, False otherwise
    """
    return validate_ipv4_network(destination) and validate_ipv4_address(gateway)