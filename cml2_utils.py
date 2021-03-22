import urllib3
from virl2_client import ClientLibrary
import os
from dotenv import load_dotenv
load_dotenv()


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

client = ClientLibrary(os.getenv("CML_URL"), "admin", os.getenv("CML_PASS"), ssl_verify=False)

print(client)

.replace("GigabitEthernet1", "s0")
                    .replace("GigabitEthernet2", "s1")
                    .replace("GigabitEthernet3", "s2")
                    .replace("GigabitEthernet4", "s3")
                    .replace("GigabitEthernet5", "s4")
                    .replace("GigabitEthernet6", "s5")
                    .replace("mgmt0", "s0")