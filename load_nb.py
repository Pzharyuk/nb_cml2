from nb_utils import *

# Lab Name variable
lab_name = "pdx-cloud-test"

# Manufacturer name
manufacturer = "cisco"

# Managment interface dictionary
mgmt_intf =  {
    "iosv": "GigabitEthernet0",
    "csr1000v": "GigabitEthernet1",
    "nxos": "mgmt0"
}

# Platform list
platform = {
    "ios": "ios",
    
    "nxos": "nxos"
}

# Check and add platform if needed
create_platform = device_platform(platform['ios'])

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
ios_config = jinja2_conf_gen(ip,hostname,mgmt_intf['iosv'],platform['ios'])