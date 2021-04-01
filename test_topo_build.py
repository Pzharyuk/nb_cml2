from os import read
from cml2_utils import cml_create_lab_topology

tag = "pdx-man-test"

# read_files = cml_read_config_files()

nodes = {
"AZURE1": "csr1000v",
"AZURE2": "iosv",
"CLOUD1": "iosvl2",
"CLOUD2": "nxosv",
"CLOUD4": "iosxe-sdwan"
}
 
# read_files = cml_read_config_files()

# for k,v in nodes.items():
#     for files in read_files:
#         if k in files:
#             print(files)
        
create_lab = cml_create_lab_topology(tag,nodes)