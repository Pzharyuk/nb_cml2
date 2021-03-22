
__author__ = "Paul Zharyuk"
__status__ = "Lab"

#from platform import platform
import pynetbox
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import os
import itertools
import sys
from jinja2 import Template
from rich.console import Console
from netaddr import IPAddress
from netaddr import IPNetwork
from rich.table import Table
from dotenv import load_dotenv
load_dotenv()

console = Console()
sys.tracebacklimit = 0

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

nb_lab = pynetbox.api(
    os.getenv("NB_LAB_URL"),
    token=os.getenv("NB_LAB_TOKEN")
)
nb_lab.http_session = session


device_roles = {
    "CSR1000v": "router",
    "IOSv": "router",
    "ASAv": "firewall",
    "NX-OSv 9000": "switch",
    "IOSvL2": "switch",
    "OTHER": "other",
}

def tag(tag):
    """ Lookup tag and create one if it doesn't exist """
    tag_lookup = nb_lab.extras.tags.filter(name=f"{tag}")
    if not tag_lookup:
        nb_lab.extras.tags.create(
            name=f"{tag}",
            slug=f"{tag}")
    tag_id = nb_lab.extras.tags.get(name=f"{tag}")
    return tag_id.id

def ip_payload(hostname,tag_id):
    """ Json body used to create IP's """
    payload = []
    for h in hostname:
        payload.append(
            {
            "dns_name": f"{h}",
            "tenant": 1,
            "tags": [
                f"{tag_id}"
            ]
            }
        )
    return payload

def nb_lab_manufacturer(name):
    nb_manufacturer = nb_lab.dcim.manufacturers.get(name=name)
    if nb_manufacturer is None:
        # Create a slug from the name
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace(",", "-")
            .replace(".", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        nb_manufacturer = nb_lab.dcim.manufacturers.create(
            name=name, slug=slug
        )
    return nb_manufacturer
    
def device_platform(pltfrm):
    """Get or Create a nb_lab Device Platform"""
    for p in pltfrm:
        nb_platform = nb_lab.dcim.platforms.get(name=p)
        if nb_platform is None:
            # Create slug from name
            slug = (
                p.lower()
                .replace(" ", "-")
                .replace(",", "-")
                .replace(".", "_")
                .replace("(", "_")
                .replace(")", "_")
            )
            nb_platform = nb_lab.dcim.platforms.create(name=p, slug=slug)
        return nb_platform

def get_interface(tag):
    """ Get interfaces that are tagged with lab name and replace name to match CML2 """
    interface = []
    interfaces = nb_lab.dcim.interfaces.filter(tag=tag)
    for int in interfaces:
        interface.append(int.name)
    return(interface)

# def get_device(tag):
#     hostname = []
#     devices = nb_lab.dcim.devices.filter(tag=tag)
#     for h in devices:
#         hostname.append(h['name'])
#     return hostname

# def get_platform(tag):
#     pltfrm = []
#     platform = nb_lab.dcim.devices.filter(tag=tag)
#     for h in platform:
#          pltfrm.append(h['platform']['name'])
#     return pltfrm

def get_prefix_id(tag):
    prefix = nb_lab.ipam.prefixes.get(tag=f"{tag}")
    prefix_id = prefix.id
    return(prefix_id)

def allocate_ip(prefix_id,hostname,payload):
    """ Get gateway IP from nb_lab and allocate IP's """
    gateway = nb_lab.ipam.ip_addresses.get(tag="cml2_gateway")
    ip = []
    try:
        prefix = nb_lab.ipam.prefixes.get(f"{prefix_id}")
        console.print("[bold magenta]Prefix is: {}[/bold magenta]".format(prefix))
        available_ip = prefix.available_ips.list()
        for (i,b) in itertools.zip_longest(range(len(hostname)),payload):
            create = prefix.available_ips.create(b)
            ip.append(IPNetwork(create.address))
            # PRINT COLLECTED IP/MASK VARIABLES TO SCREEN
            console.print("[bold green]Hostname is: {}[/bold green]".format(create.dns_name))
            console.print("[bold green]IP is: {}[/bold green]".format(create.address))
            console.print("[bold green]Gateway is: {}[/bold green]".format(gateway.address[:-3]))
    except p nb_lab.core.query.RequestError as e:
        console.print("[bold red]{}[/bold red]".format(e.error))
    return ip
        
def jinja2_conf_gen(ip,hostname,interface,pltfrm):
    """ Generate configs using Jinja2 """
    gateway = nb_lab.ipam.ip_addresses.get(tag="cml2_gateway")
    cml2_vars = []
    for (a,b) in itertools.zip_longest(ip,hostname):
        cml2_vars.append(
            dict(
                mask = a.netmask,
                ip = a.ip,
                hostname = f"{b}",
                interface = f"{interface}",
                gateway = f"{gateway.address[:-3]}"
            )
        )
        
    if pltfrm == "ios": 
        with open("./templates/cml2_ios_confgen.j2") as f:
            cml_template = Template(f.read())
        for (h,v) in itertools.zip_longest(hostname,cml2_vars):
            with open(f"configs/{h}_startup.config", 'w') as f:
                config_out = cml_template.render(data=v)
                f.write(config_out)
    elif pltfrm == "iosxe":
        with open("./templates/cml2_ios_confgen.j2") as f:
            cml_template = Template(f.read())
        for (h,v) in itertools.zip_longest(hostname,cml2_vars):
            with open(f"configs/{h}_startup.config", 'w') as f:
                config_out = cml_template.render(data=v)
                f.write(config_out)
    elif pltfrm == "nxos":
        with open("./templates/cml2_nxos_confgen.j2") as f:
            cml_template = Template(f.read())
        for (h,v) in itertools.zip_longest(hostname,cml2_vars):
            with open(f"configs/{h}_startup.config", 'w') as f:
                config_out = cml_template.render(data=v)
                f.write(config_out)
    else:
        print("Platform specified is not available")