from nb_utils import *
from cml2_utils import cml_get_node_definitions
from nb_utils import *

""" 
Node Definitions

Management:
external_connector | unmanaged_switch

Routers:
csr1000v | iosv | iosxrv | iosxrv900

Switches: 
iosvl2  | nxosv9000 | nxosv

Servers: 
alpine | linux | server | coreos | desktop | ubuntu 0

Firewall:
asav 

SDWAN:
viptela-smart | viptela-bond | viptela-edge | iosxe-sdwan

"""


# Lab Name variable
lab_name = "pdx-cloud-test"

# Dictioary of hostnames + nodes definition to be used in the topology 
nodes = {
    "AZURE1": "csr1000v",
    "AZURE2": "iosv",
    "CLOUD1": "iosvl2",
    "CLOUD2": "nxosv",
    "CLOUD4": "iosxe-sdwan"
}

# Platform list used to generate jinja configs based on platform
platform = []

for k,v in nodes.items():
    get_node_details = cml_get_node_definitions(v)
    for g in get_node_details:
        platform.append(g['device_platform'])
        tag = nb_tag(lab_name)
        site = nb_site(lab_name)
        dev_manufacturer = nb_device_manufacturer(g['device_manufacturer'])
        dev_type = nb_device_type(g['device_type'],dev_manufacturer)
        dev_platform = nb_device_platform(g['device_platform'])
        dev_role = nb_device_role(g['device_role'])
        device = nb_device(site,dev_type,k,tag)

# Get hostnames
hostname = nodes.keys()
# Get or create tag with lab name        
tag_id = nb_tag(lab_name)
# Get prefix id
prefix_id = nb_get_prefix_id("cml2") # Get the prefix ID      
# Create payload for Netbox IP allocation
payload = nb_ip_payload(nodes.keys(),tag_id.id)
# Allocate IP's in Netbox
ip = nb_allocate_ip(prefix_id,nodes.keys(),payload)
# Generate configs using Jinja2
ios_config = nb_jinja2_conf_gen(ip,hostname,platform)
