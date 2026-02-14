from helper import display_interfaces, execute_command, get_interfaces, validate_input, validate_ipv4_network, validate_ipv4_address, get_routes, validate_route
from strings import Strings
import ipaddress

def set_static_ip(interface, ip_address):
    try:
        execute_command(f'sudo nmcli con modify {interface} ipv4.addresses {ip_address} ipv4.method manual')
        print(f"Successfully set static IP {ip_address} on {interface}")
    except Exception as e:
        print(f"Failed to set static IP: {e}")

def fix_all_interface():
    try:
        output = execute_command("nmcli -g NAME,DEVICE connection show")
        connections = [line.split(":") for line in output.splitlines() if line]
        for conn_name, device in connections:
            execute_command(f'sudo nmcli con modify "{conn_name}" con-name {device}', suppress_errors=True)
    except Exception as e:
        print(f"Warning: Failed to fix interface names: {e}")

def add_static_route(interface, destination, gateway):
    """Add a static route to an interface."""
    try:
        if not validate_route(destination, gateway):
            print("Invalid route configuration")
            return False
        
        execute_command(f'sudo nmcli con modify {interface} +ipv4.routes "{destination} {gateway}"')
        print(f"Successfully added route: {destination} via {gateway} on {interface}")
        return True
    except Exception as e:
        print(f"Failed to add static route: {e}")
        return False

def view_routes(interface=None):
    """View current routing table."""
    print("\n=== Current Routing Table ===")
    routes = get_routes(interface)
    if routes:
        print(routes)
    else:
        print("No routes found or failed to retrieve routes")
    print("============================\n")

def delete_static_route(interface):
    """Delete a static route from an interface."""
    try:
        # First, show current routes for this interface
        print(f"\nCurrent routes configured on {interface}:")
        output = execute_command(f'nmcli -g ipv4.routes connection show {interface}', check=False, suppress_errors=True)
        
        if not output or output.strip() == '':
            print("No static routes configured on this interface")
            return False
        
        print(output)
        
        route_to_delete = validate_input(
            "Enter the route to delete (e.g., 192.168.1.0/24 192.168.1.1) or 'q' to cancel: ",
            lambda x: x == 'q' or (len(x.split(" ")) == 2 and validate_route(x.split(" ")[0], x.split(" ")[1]))
        )
        
        if route_to_delete == 'q':
            print("Route deletion cancelled")
            return False
        
        destination, via = route_to_delete.split(" ")
        execute_command(f'sudo nmcli con modify {interface} -ipv4.routes "{destination} {via}"')
        print(f"Successfully deleted route: {destination} via {via}")
        return True
        
    except Exception as e:
        print(f"Failed to delete static route: {e}")
        return False

def main():
    fix_all_interface()
    print(Strings.Interface.main_help)
    interfaces = get_interfaces()
    display_interfaces()
    while True:
        choice = validate_input("Select an interface by number (use lo to configure bridge): ", 
                                lambda x: x == "q" or (x.isdigit() and 1 <= int(x) <= len(interfaces)))
        if choice == "q":
            print("Exiting interface configuration.")
            break
        
        selected_interface = interfaces[int(choice) - 1]
        if selected_interface == "lo":
            # we use this to configure bridge
            bridge_name = validate_input("Enter bridge name: ", lambda x: len(x) > 0)
            display_interfaces()
            slaves = validate_input("Enter interfaces to add to bridge (space separated), you must enter the full interface names: ", lambda x: all(iface in interfaces for iface in x.split()))
            slave_list = slaves.split()
            execute_command(f" nmcli con add type bridge con-name {bridge_name} ifname {bridge_name}")
            for slave in slave_list:
                execute_command(f"nmcli con add type ethernet slave-type bridge con-name {slave} ifname {slave} master {bridge_name}")
            execute_command(f'nmcli con modify {bridge_name} connection.autoconnect-slaves 1')
            execute_command(f'nmcli con up {bridge_name}')
        execute_command(f'sudo nmcli con up {selected_interface} ifname {selected_interface}')
        print(Strings.Interface.nmcli_options)
        option = validate_input("Enter your choice (1-7): ", 
                                lambda x: x in ['1', '2', '3', '4', '5', '6', '7'])
        if option == '1':
            static_ip = validate_input("Enter static IP (e.g., 192.168.1.100/24): ", validate_ipv4_network)
            set_static_ip(selected_interface, static_ip)
        elif option == '2':
            try:
                command = f'sudo nmcli con modify {selected_interface} ipv4.method auto'
                execute_command(command)
                print(f"Successfully set {selected_interface} to DHCP mode")
            except Exception as e:
                print(f"Failed to set DHCP: {e}")
        elif option == '3':
            try:
                gateway = validate_input("Enter gateway IP: ", validate_ipv4_address)
                dns = validate_input("Enter DNS server IP: ", validate_ipv4_address)
                execute_command(f'sudo nmcli con modify {selected_interface} ipv4.gateway {gateway}')
                execute_command(f'sudo nmcli con modify {selected_interface} ipv4.dns {dns}')
                print(f"Successfully configured gateway {gateway} and DNS {dns} on {selected_interface}")
            except Exception as e:
                print(f"Failed to configure gateway/DNS: {e}")
        elif option == '4':
            route = validate_input("Enter static route (e.g., 192.168.1.0/24 192.168.1.1): ", lambda x: len(x.split(" ")) == 2 and validate_ipv4_network(x.split(" ")[0]) and validate_ipv4_address(x.split(" ")[1]))  
            destination, via = route.split(" ")
            add_static_route(selected_interface, destination, via)
        elif option == '5':
            view_routes(selected_interface)
        elif option == '6':
            delete_static_route(selected_interface)
        elif option == '7':
            pass
        execute_command(f'sudo nmcli con up {selected_interface}')
        execute_command('sudo nmcli con reload')

if __name__ == "__main__":
    main()