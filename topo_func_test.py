
import urllib3
from virl2_client import ClientLibrary
import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
url = "https://192.220.250.2/api/v0"

client = ClientLibrary("https://192.220.250.2", "admin", os.getenv("CML_PASS"), ssl_verify=False)

lab_list = client.get_lab_list(show_all=True)


def cml_read_config_files():
    # Collect files inside the config directory and sort them in order
    file_names = []

    paths = Path('configs').glob('*.config')
    for path in paths:
        # because path is object not string
        path_in_str = str(path)
        # Do thing with the path
        file_names.append(path_in_str)

    sorted_files =  sorted(file_names)

    # Read each file inside the config directory
    config_files = [] 
    for file in sorted_files:    
        f = open(f"{file}", "r")
        config_files.append(f.read())
        
    return config_files
    
################################################################################################
# lab = client.join_existing_lab("cace9c")
# testbed_yaml = lab.get_pyats_testbed()
# nodes = client.definitions.node_definitions()
# for n in nodes:
#     print(n)
#get_lab_title = client.find_labs_by_title(tag)

def cml_create_lab_topology(tag,nodes):
    
    nodes = {
    "AZURE1": "csr1000v",
    "AZURE2": "iosv",
    "CLOUD1": "iosvl2",
    "CLOUD2": "nxosv",
    "CLOUD4": "iosxe-sdwan"
    }
    
    read_files = cml_read_config_files()
            
    lab = client.create_lab(title=tag)

    ext = lab.create_node("EXT-MGMT", "external_connector", 0, 50)
    ext.add_tag(tag)
    ext.config = "bridge0"
    oob_sw = lab.create_node("OOB", "unmanaged_switch", 0, 150)
    for k,v in nodes.items():
        for files in read_files:
            if k in files:
                position = 50
                node = lab.create_node(k, v, -100, 200)
                node.config = k
        cloud2 = lab.create_node("azure2", "iosv", 100, 250)
        cloud2.config = f"{config_files[1]}"
        azure1 = lab.create_node("cloud1", "iosv", -100, 350)
        azure1.config = f"{config_files[2]}"
        azure2 = lab.create_node("cloud2", "iosv", 100, 350)
        azure2.config = f"{config_files[3]}"

        # management links
        ext_i0 = ext.create_interface(slot=0)
        oob_i0 = oob.create_interface(slot=0)
        oob_i1 = oob.create_interface(slot=1)
        oob_i2 = oob.create_interface(slot=2)
        oob_i3 = oob.create_interface(slot=3)
        oob_i4 = oob.create_interface(slot=4)
        cloud1_i0 = cloud1.create_interface(slot=0)
        cloud2_i0 = cloud2.create_interface(slot=0)
        azure1_i0 = azure1.create_interface(slot=0)
        azure2_i0 = azure2.create_interface(slot=0)

        # inter router links
        cloud1_i1 = cloud1.create_interface(slot=1)
        cloud2_i1 = cloud2.create_interface(slot=1)
        cloud1_i2 = cloud1.create_interface(slot=2)
        cloud2_i2 = cloud2.create_interface(slot=2)
        azure1_i1 = azure1.create_interface(slot=1)
        azure2_i1 = azure2.create_interface(slot=1)
        azure1_i2 = azure1.create_interface(slot=2)
        azure2_i2 = azure2.create_interface(slot=2)

        # managment links to OOB switch from each router
        lab.create_link(ext_i0, oob_i0)
        lab.create_link(oob_i1, cloud1_i0)
        lab.create_link(oob_i2, cloud2_i0)
        lab.create_link(oob_i3, azure1_i0)
        lab.create_link(oob_i4, azure2_i0)

        # inter-router links
        lab.create_link(cloud1_i1, cloud2_i1)
        lab.create_link(cloud1_i2, azure1_i2)
        lab.create_link(cloud2_i2, azure2_i2)

