import urllib3
from virl2_client import ClientLibrary
import os
from dotenv import load_dotenv
from pathlib import Path
from numpy import random
load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

client = ClientLibrary(
    os.getenv("CML_URL"),
    "admin", os.getenv("CML_PASS"), 
    ssl_verify=False)

#Download lab from CML2
# join_lab = client.join_existing_lab("edaee3")
# download = join_lab.download

# with open(f"./{join_lab.title}.yaml", "w") as file:
#     file.write(download)

#Import lab to CML2
with open(f"./pdx-cloud-test.yaml", "r") as file:
    data = file.read()
    
client.import_lab(data, "pdx-cloud-test")

