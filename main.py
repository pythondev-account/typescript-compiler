from dhcp import main as dhcp_main
from interface import main as interface_main
from bird import main as bird_main
import os

def main():
    if os.geteuid() != 0:
        print("This script must be run as root. Please run with sudo.")
        exit(1)
    while True:
        print("Select configuration to perform:")
        print("1. Network Interface Configuration")
        print("2. DHCP Server Configuration")
        print("3. BIRD OSPF Configuration")
        print("q. Quit")
        choice = input("> ")
        if choice == '1':
            interface_main()
        elif choice == '2':
            dhcp_main()
        elif choice == '3':
            bird_main()
        elif choice.lower() == 'q':
            print("Exiting configuration tool.")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()