from cml2_utils import cml_get_node_definitions
from nb_utils import *
import itertools

lab_name = "pdx_test"

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


nodes = {
    "AZURE1": "csr1000v",
    "AZURE2": "iosv",
    "CLOUD1": "iosvl2",
    "CLOUD2": "nxosv9000"
}


for k,v in nodes.items():
    get_node_details = cml_get_node_definitions(v)
    for g in get_node_details:
        print(g['device_type'])
        for int in g['device_intf']:
            print(int)
        # test_tag = nb_tag(lab_name)
        # test_site = nb_site(lab_name)
        # test_dev_manufacturer = nb_device_manufacturer(g['device_manufacturer'])
        # test_dev_type = nb_device_type(g['device_type'],test_dev_manufacturer)
        # test_dev_platform = nb_device_platform(g['device_type'])
        # test_dev_role = nb_device_role(g['device_role'])
        # test_device = nb_device(test_site,test_dev_type,k,test_tag)
    