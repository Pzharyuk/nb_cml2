import urllib3
from virl2_client import ClientLibrary
import os
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

client = ClientLibrary(
    os.getenv("CML_URL"),
    "admin", os.getenv("CML_PASS"), 
    ssl_verify=False)

def get_config_files():
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

