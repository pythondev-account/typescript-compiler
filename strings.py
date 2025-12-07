class Strings:
    class DHCP:
        main_help = """
Configure Kea DHCP, please read the options carefully:

Press a to add entry: Add a new DHCP configuration entry.
Press n to reset all DHCP config: Clear all current DHCP configurations.
Press m to save DHCP config and reload DHCP server
Press p to preview your changes
"""
        dhcp_json_failure = """
Failed to parse DHCP configuration JSON. Perhaps there are # comments in the files. Python do not support comments in JSON. You should make a backup of the file before proceeding.
"""

        main_input = "Enter choice (a: add, n: reset, m: commit, p: preview): "

        input_subnet = """
Enter your subnet in CIDR notation (e.g., 192.168.1.0/24):
> """
        input_reservation = """
Enter DHCP reservation in this format, MAC address and static IP address separated by a single space e.g., 
00:1A:2B:3C:4D:5E 192.168.1.100
2 192.168.1.102 will correspond to MAC address 00:00:00:00:00:02

If you are done adding reservations or do not wish to add any, just press enter."""
    class Interface:
        main_help = """
This utility will help you configure networking interfaces configuration using nmcli. You'll need to select a network interface to continue.
"""
        nmcli_options = """
Choose an option for your network interface configuration:
1. Set Static IP
2. Set DHCP
3. Setup gateway and DNS
4. Add Static Route
"""
    class Bird:
        router_id_prompt = "Error occured with getting Router ID. Please enter a valid Router ID, you can check your Router ID with an IPv4 address: "