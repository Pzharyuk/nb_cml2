
__author__ = "Paul Zharyuk"
__status__ = "Lab"

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
import itertools
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

# Dictionary of common device roles in CML
device_roles = {
    "CSR1000v": "router",
    "CSR1000V": "router",
    "IOSv": "router",
    "ASAv": "firewall",
    "NX-OSv 9000": "switch",
    "NX-OS 9000": "switch",
    "NX-OS": "switch",
    "IOSvL2": "switch",
    "vBond": "server",
    "vSmart": "server",
    "vManage": "server",
    "vEdge": "server",
    "XE-SDWAN": "router",
    "OTHER": "other"
}

# Dictionary of common CML2 node management interfaces """
mgmt_intf =  {
    "ios": "GigabitEthernet0",
    "iosxe": "GigabitEthernet1",
    "nxos": "mgmt0",
    "iosxrv900": "MgmtEth0/RP0/CPU0/0",
    "asav": "Management0/0",
    "iosxe-sdwan": "GigabitEthernet1"
}

""" Interface types. """
FF_1000BASE_T = 1000
FF_SFPPLUS = 1200
FF_OTHER = 32767


def nb_ip_payload(hostname,tag_id):
    """ Body template used to generate IP's in Netbox. """
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


def nb_tag(name):
    """ Lookup a tag and create one if it does not exist. """
    tag_lookup = nb_lab.extras.tags.filter(name=name)
    if not tag_lookup:
        nb_lab.extras.tags.create(
            name=name,
            slug=name)
    tag_id = nb_lab.extras.tags.get(name=name)
    return tag_id

def nb_site(name):
    """ Get or Create a Netbox site object. """
    tag = nb_tag(name)
    nb_site = nb_lab.dcim.sites.get(name=name)
    if nb_site is None:
        # Create a slug from the name
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace(",", "-")
            .replace(".", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        nb_site = nb_lab.dcim.sites.create(
            name=name, 
            slug=slug, 
            status="active",
            tags=[tag.id],
        )
    return nb_site

def nb_device_role(name):
    """ Get or Create a Netbox device role. """
    nb_role = nb_lab.dcim.device_roles.get(name=name)
    if nb_role is None:
        # Create a slug from the name
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace(",", "-")
            .replace(".", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        """ Set device role and color based on role. """
        if name == "router":
            nb_role = nb_lab.dcim.device_roles.create(
                name=name, slug=slug, color="c0c0c0")
        elif name == "switch":
            nb_role = nb_lab.dcim.device_roles.create(
                name=name, slug=slug, color="673ab7"
        )
        elif name == "server":
            nb_role = nb_lab.dcim.device_roles.create(
                name=name, slug=slug, color="3ab3b7"
        )
        elif name == "firewall":
            nb_role = nb_lab.dcim.device_roles.create(
                name=name, slug=slug, color="e00202"
        )
        elif name == "other":
            nb_role = nb_lab.dcim.device_roles.create(
                name=name, slug=slug, color="e00271"
        )
        else:
            nb_role = nb_lab.dcim.device_roles.create(
                name=name, slug=slug, color="02e071"
        )
    return nb_role

def nb_device_manufacturer(manufacturer):
    """ Get or create Netbox device manufacturer. """
    nb_manufacturer = nb_lab.dcim.manufacturers.get(slug=manufacturer.lower())
    if nb_manufacturer is None:
        # Create a slug from the name
        man_slug = (
            manufacturer.lower()
            .replace(" ", "-")
            .replace(",", "-")
            .replace(".", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        nb_manufacturer = nb_lab.dcim.manufacturers.create(
            name=manufacturer, slug=man_slug
        )
    else:
        return nb_manufacturer
    
def nb_device_platform(name):
    """Get or Create Netbox device platform"""
    nb_platform = nb_lab.dcim.platforms.get(name=name)
    if nb_platform is None:
        # Create slug from name
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace(",", "-")
            .replace(".", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        nb_platform = nb_lab.dcim.platforms.create(name=name, slug=slug)
        return nb_platform
    
def nb_device_type(cml_device_type,manufacturer):
    """ Get or create dervice type in Netbox. """
    nb_device_type = nb_lab.dcim.device_types.get(slug=cml_device_type.lower())
    if nb_device_type is None:
        slug=(
            str(cml_device_type).lower()
            .replace(" ", "-")
            .replace(",", "-")
            .replace(".", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        nb_device_type = nb_lab.dcim.device_types.create(
                manufacturer=manufacturer.id,
                model=cml_device_type,
                slug=slug,
                u_height=1,
            )
    return nb_device_type
        
def nb_device(site,type,hostname,tag):
    """Get or Create a device in netbox based on lab requirements."""
    # See if device exists, if not create one.
    nb_device = nb_lab.dcim.devices.get(name=hostname)
    if nb_device is None:
    # Get the device role based on type. If not defined, set to "OTHER"
        if type.model in device_roles:
            role = nb_device_role(device_roles[type.model])
        else:
            role = nb_device_role(device_roles['OTHER'])
            # Create the device in netbox
        device = nb_lab.dcim.devices.create(
            name=hostname,
            device_type=type.id,
            device_role=role.id,
            site=site.id,
            status="active",
            tags=[tag.id],
        )
    return nb_device

def nb_device_interface(nb_device, interface_name, interface_description="", mgmt_only=False):
    """Create and update a Netbox interface object for a device."""
    # See if the interface exists
    nb_interface = nb_lab.dcim.interfaces.filter(
        device=nb_device.name, name=interface_name
    )
    # See if single item returned, if so, set to value
    if len(nb_interface) == 1:
        nb_interface = nb_interface[0]
    # Create Interface
    elif nb_interface is None or len(nb_interface) == 0:
        # Create New Interface
        nb_interface = nb_lab.dcim.interfaces.create(
            device=nb_device.id,
            name=interface_name,
            form_factor=FF_OTHER,
            enabled=True,
            mgmt_only=mgmt_only,
            description=interface_description,
        )
    else:
        print("More than one interface found.. that is odd.")
    return nb_interface

# def nb_get_interface(tag):
#     """ Get interfaces that are tagged with lab name and replace name to match CML2 """
#     interface = []
#     interfaces = nb_lab.dcim.interfaces.filter(tag=tag)
#     for int in interfaces:
#         interface.append(int.name)
#     return(interface)

def nb_get_prefix_id(tag):
    prefix = nb_lab.ipam.prefixes.get(tag=f"{tag}")
    prefix_id = prefix.id
    return(prefix_id)

def nb_allocate_ip(prefix_id,hostname,payload):
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
    except pynetbox.RequestError as e:
        console.print("[bold red]{}[/bold red]".format(e.error))
    return ip
        
def nb_jinja2_conf_gen(ip,hostname,platform):
    """ Generate configs using Jinja2 """
    gateway = nb_lab.ipam.ip_addresses.get(tag="cml2_gateway")
    cml2_vars = []
    for (i,h,p) in itertools.zip_longest(ip,hostname,platform):
        if p in mgmt_intf:
            cml2_vars.append(
                dict(
                    mask = i.netmask,
                    ip = i.ip,
                    hostname = h,
                    interface = mgmt_intf[p],
                    gateway = f"{gateway.address[:-3]}"
                )
            )
    for (h,v,p) in itertools.zip_longest(hostname,cml2_vars,platform):    
        if p == "ios": 
            with open("./templates/cml2_ios_confgen.j2") as f:
                cml_template = Template(f.read())
            with open(f"configs/{h}_startup.config", 'w') as f:
                config_out = cml_template.render(data=v)
                f.write(config_out)
        elif p == "iosxe":
            with open("./templates/cml2_ios_confgen.j2") as f:
                cml_template = Template(f.read())
            with open(f"configs/{h}_startup.config", 'w') as f:
                config_out = cml_template.render(data=v)
                f.write(config_out)
        elif p == "nxos":
            with open("./templates/cml2_nxos_confgen.j2") as f:
                cml_template = Template(f.read())
            with open(f"configs/{h}_startup.config", 'w') as f:
                config_out = cml_template.render(data=v)
                f.write(config_out)
        elif p == "iosxe-sdwan":
            with open("./templates/cml2_ios_confgen.j2") as f:
                cml_template = Template(f.read())
            with open(f"configs/{h}_startup.config", 'w') as f:
                config_out = cml_template.render(data=v)
                f.write(config_out)
        else:
            print("Platform specified is not available")