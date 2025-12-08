from helper import display_interfaces, execute_command, get_interfaces, validate_input, validate_ipv4_network, validate_ipv4_address
from strings import Strings
import ipaddress

def set_static_ip(interface, ip_address):
    execute_command(f'sudo nmcli con up {interface} ifname {interface}')    
    execute_command(f'sudo nmcli con modify {interface} ipv4.addresses {ip_address} ipv4.method manual')

def main():
    print(Strings.Interface.main_help)
    interfaces = get_interfaces()
    display_interfaces()
    while True:
        choice = validate_input("Select an interface by number: ", 
                                lambda x: x == "q" or (x.isdigit() and 1 <= int(x) <= len(interfaces)))
        if choice == "q":
            print("Exiting interface configuration.")
            break
        selected_interface = interfaces[int(choice) - 1]
        execute_command(f'sudo nmcli con up {selected_interface} ifname {selected_interface}')
        print(Strings.Interface.nmcli_options)
        option = validate_input("Enter your choice (1-4): ", 
                                lambda x: x in ['1', '2', '3', '4'])
        if option == '1':
            static_ip = validate_input("Enter static IP (e.g., 192.168.1.100/24): ", validate_ipv4_network)
            set_static_ip(selected_interface, static_ip)
        elif option == '2':
            command = f'sudo nmcli con modify {selected_interface} ipv4.method auto'
            execute_command(command)
        elif option == '3':
            gateway = validate_input("Enter gateway IP: ", validate_ipv4_address)
            dns = validate_input("Enter DNS server IP: ", validate_ipv4_address)
            execute_command(f'sudo nmcli con modify {selected_interface} ipv4.gateway {gateway}')
            execute_command(f'sudo nmcli con modify {selected_interface} ipv4.dns {dns}')
        elif option == '4':
            route = validate_input("Enter static route (e.g., 192.168.1.0/24 192.168.1.1): ", lambda x: len(x.split(" ")) == 2 and validate_ipv4_network(x.split(" ")[0]) and validate_ipv4_address(x.split(" ")[1]))  
            destination, via = route.split(" ")
            execute_command(f'sudo nmcli con modify {selected_interface} +ipv4.routes "{destination} {via}"')

        execute_command(f'sudo nmcli con up {selected_interface}')
        execute_command('sudo nmcli con reload')

if __name__ == "__main__":
    main()