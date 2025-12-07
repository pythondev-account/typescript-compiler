import os
from helper import read_file, execute_command, validate_input, get_interfaces, display_interfaces, validate_ipv4_address
from strings import Strings

class OSPF:
    def __init__(self, interface, is_stub=False):
        self.interface = interface
        self.stub = is_stub

    def __repr__(self):
        return f"OSPF(interface={self.interface}, is_stub={self.stub})"
    
    def export(self):
        return f"""
      interface "{self.interface}" {{
        {'stub;' if self.stub else ''}
      }}
"""
    
base_bird_config = """
# /etc/bird.conf

log syslog all;             # Log all messages
"""
base_bird_router_id = "router id {router_id};"

base_bird_pre="""
protocol device {           
}

protocol kernel {
    ipv4 {                  # export all routes learned by bird to the kernel
          export all;       # routing table
    };
}

protocol ospf {            # Activate OSPF
    area 0 {
"""
base_bird_post="""
    };
}
"""

def generate_bird_config(router_id, ospf_configs):
    return base_bird_config + base_bird_router_id.format(router_id=router_id) + base_bird_pre + "\n".join([ospf.export() for ospf in ospf_configs]) + base_bird_post

def main():
    interfaces = get_interfaces()
    display_interfaces()
    router_id = execute_command("ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'")
    if not validate_ipv4_address(router_id):
        router_id = validate_input(Strings.Bird.router_id_prompt, validate_ipv4_address)
    ospf_participants = input("Enter OSPF participants' index as displayed (leave blank if none):\n> ")
    ospf_stubs = input("Enter OSPF interface indexes to be marked as stub (leave blank if none):\n> ")
    ospf_list = ospf_participants.split() if ospf_participants else []
    ospf_configs = []
    for ospf in ospf_list:
        try:
            interface_name = interfaces[int(ospf) - 1]
            is_stub = ospf in ospf_stubs.split() if ospf_stubs else False
            ospf_configs.append(OSPF(interface_name, is_stub))
        except Exception as e:
            print(f"Error occured parsing OSPF participant index {ospf}: {e}")
    bird_config = generate_bird_config(router_id, ospf_configs)
    print(bird_config)
    input("Press Enter to save the configuration to /etc/bird.conf and restart BIRD.")
    with open('/etc/bird.conf', 'w') as f:
        f.write(bird_config)
    execute_command('sudo bird -p')
    execute_command('systemctl restart bird')

if __name__ == "__main__":
    main()