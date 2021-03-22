from nb_utils import *

# Manufacturer name
manufacturer = "cisco"

# List of management interfaces
mgmt_intf = [
    "GigabitEthernet0",
    "GigabitEthernet1",
    "mgmt0" 
    ]
# Lab Name variable
lab_name = "pdx-cloud-test"

# Platform list
pltfrm = [
    "ios",
    "iosxe",
    "nxos"
    ]

# Check and add platform if needed
create_platform = device_platform(pltfrm[0])

# Check if manufacturer exisist, if not create it
create_manufacturer = nb_lab_manufacturer(manufacturer)

# Create a list of devices to be used in the lab
hostname = [
    "AZURE1",
    "AZURE2",
    "CLOUD1",
    "CLOUD2",
]

# Get prefix id
prefix_tag = "cml2" # The prefix is tagged with cml2, makes it easy to retrieve
prefix_id = get_prefix_id(f"{prefix_tag}") # Get the prefix ID


# Check if tag with lab name exist, if not create it
tag_id = tag(f"{lab_name}")

# Create payload for Netbox IP allocation
payload = ip_payload(hostname,tag_id)

# Allocate IP's in Netbox
ip = allocate_ip(prefix_id,hostname,payload)

# Generate configs using Jinja2
ios_config = jinja2_conf_gen(ip,hostname,mgmt_intf[1],pltfrm[0])