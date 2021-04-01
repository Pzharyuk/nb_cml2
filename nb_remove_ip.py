import pynetbox
from nb_utils import nb_lab
from rich.console import Console
from rich.table import Table
import sys

console = Console()
sys.tracebacklimit = 0

# EMPTY LISTS TO BE USED LATER IN THE CODE #
lab_name = "pdx-cloud-test"
# GET ID BASED ON TAG #
try:
    id_dict = {
        "ip": nb_lab.ipam.ip_addresses.filter(tag=f"{lab_name}"),
        "site": nb_lab.dcim.sites.get(tag=f"{lab_name}"),
        "device": nb_lab.dcim.devices.filter(tag=f"{lab_name}") 
        }
except pynetbox.RequestError as e:
    print(e.error)
    
try:    
    for id in id_dict['device']:
        device_delete = nb_lab.dcim.devices.get(id.id) 
        device_delete.delete()
        
except pynetbox.RequestError as e:
    print(e.error)

try:       
    site_id = id=id_dict['site']['id']
    delete_site = nb_lab.dcim.sites.get(site_id)
    delete_site.delete()
except TypeError as e:
    print(f"Site does not exist - Error: {e}")

try:    
    for ids in id_dict['ip']:
        delete_ip = nb_lab.ipam.ip_addresses.get(ids.id)
        delete_ip.delete()
        #print(delete_ip)
        console.print("[bold red]IP Address: {} has been removed...[/bold red]".format(delete_ip,ids))
except pynetbox.RequestError as e:
    print(e.error)
