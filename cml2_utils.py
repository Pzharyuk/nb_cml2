import urllib3
from virl2_client import ClientLibrary
import os
from dotenv import load_dotenv
from pathlib import Path
from numpy import random
import itertools
load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

client = ClientLibrary(
    os.getenv("CML_URL"),
    "admin", os.getenv("CML_PASS"), 
    ssl_verify=False)

def cml_get_config_files():
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

def cml_get_node_definitions(nodes):
    data = client.definitions.node_definitions()
    intf = []
    cml_node = []
    for d in data:
        if d['id'] == nodes:
            for i in d['data']['device']['interfaces']['physical']:
                intf.append(i)
            try:
                cml_node.append(
                    dict(
                        device_platform = d['data']['pyats']['os'],
                        device_manufacturer = d['data']['ui']['group'],
                        device_role = d['data']['ui']['icon'],
                        device_type = d['data']['ui']['label'],
                        device_intf = intf
                    )
                )
            except KeyError as e:
                print(f"{d['id']} - {e}")
    return cml_node

def cml_read_config_files():
    """Collects files inside the ./config directory and sorts them in order"""
    file_names = []

    paths = Path('configs').glob('*.config')
    for path in paths:
        path_in_str = str(path)
        file_names.append(path_in_str)

    sorted_files =  sorted(file_names)

    """ Read each file inside the config directory """
    config_files = [] 
    for file in sorted_files:    
        f = open(f"{file}", "r")
        config_files.append(f.read())
        
    return config_files

def cml_create_lab_topology(tag,nodes):
    
    read_files = cml_read_config_files()
            
    lab = client.create_lab(title=tag)

    ext = lab.create_node("EXT-MGMT", "external_connector", 50, 0)
    ext.add_tag(tag)
    ext.config = "bridge0"
    oob_sw = lab.create_node("OOB", "unmanaged_switch", 50, 100)
    x = 0
    y = 100
    for k,v in nodes.items():
        for files in read_files:
            x = x - 50
            y = y + 50
            if k in files:
                node = lab.create_node(k, v, -x, y)
                node.config = files


# x=0
# y=100

# list_a=(1,2,3,4,5,6)

# for a in list_a:
#     x=x+50
#     if '5' in str(x):
#         y=y+50
#         x=x-100