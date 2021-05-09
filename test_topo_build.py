from os import read
from cml2_utils import cml_create_lab_topology

tag = "pdx-man-test"

# read_files = cml_read_config_files()

nodes = {
"AZURE1": "csr1000v",
"AZURE2": "iosv",
"CLOUD1": "iosvl2",
"CLOUD2": "nxosv"
}
 
# read_files = cml_read_config_files()
count = 0
for k,v in nodes.items():
    num_list = count + len(k)
    print(num_list)
        
create_lab = cml_create_lab_topology(tag,nodes)