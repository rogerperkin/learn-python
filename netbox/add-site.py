import re
import pynetbox
from pydantic import BaseModel, field_validator, ValidationError
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from InquirerPy import inquirer

# Configuration
NETBOX_API_URL = "http://192.168.1.182:8050/"
NETBOX_API_TOKEN = "447a200bfa1b4174533f59417854e9dafb3add08"

# Initialize pynetbox API
nb = pynetbox.api(NETBOX_API_URL, token=NETBOX_API_TOKEN)

console = Console()

class DeviceNameModel(BaseModel):
    name: str

    @field_validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[A-Z]{3}-[A-Z]+-[A-Z]+-\d+$', v):
            raise ValueError('Device name must follow the format: 3 letter site, Device Role, Device Type and then number (e.g., LON-CORE-ROUTER-1)')
        return v

def get_sites():
    return nb.dcim.sites.all()

def create_site(name):
    return nb.dcim.sites.create({
        "name": name,
        "slug": name.lower().replace(" ", "-")
    })

def display_sites(sites):
    table = Table(title="Existing Sites")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Slug", style="green")

    for site in sites:
        table.add_row(str(site.id), site.name, site.slug)

    console.print(table)

def get_or_create_site():
    create_new = Confirm.ask("Do you want to create a new site?")
    if create_new:
        site_name = Prompt.ask("Enter the name of the new site")
        site = create_site(site_name)
        console.print(f"[bold green]Created new site:[/bold green] {site.name} (ID: {site.id})")
    else:
        sites = get_sites()
        site_choices = {f"{site.name} (ID: {site.id})": site for site in sites}
        site_name = inquirer.fuzzy(
            message="Select a site:",
            choices=list(site_choices.keys())
        ).execute()
        site = site_choices[site_name]
    
    return site

def get_device_types():
    return nb.dcim.device_types.all()

def get_device_roles():
    return nb.dcim.device_roles.all()

def display_device_types_and_roles(device_types, device_roles):
    table = Table(title="Device Types")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Model", style="magenta")
    table.add_column("Manufacturer", style="green")

    for device_type in device_types:
        table.add_row(str(device_type.id), device_type.model, device_type.manufacturer.name)

    console.print(table)

    table = Table(title="Device Roles")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")

    for device_role in device_roles:
        table.add_row(str(device_role.id), device_role.name)

    console.print(table)

def create_device(site_id, name, device_type, role, tenant=None):
    data = {
        "name": name,
        "device_type": device_type,
        "role": role,
        "site": site_id,
        "tenant": tenant,
    }
    console.print(f"[bold blue]Debug Data Sent to API:[/bold blue] {data}")
    return nb.dcim.devices.create(data)

def display_created_device(device):
    table = Table(title="Created Device Details")
    table.add_column("Attribute", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Device Name", device.name)
    table.add_row("Device Type", device.device_type.model)
    table.add_row("Manufacturer", device.device_type.manufacturer.name)
    table.add_row("Role", device.role.name)
    table.add_row("Site", device.site.name)
    table.add_row("Tenant", device.tenant.name if device.tenant else "N/A")

    console.print(table)

def show_menu():
    ascii_art = Text("""
==================================================
           Welcome to Roger's NetBox Configurator
==================================================
""", style="bold blue")
    console.print(Panel(ascii_art, expand=False))

    options = ["Add a Device"]
    choice = inquirer.select(
        message="What do you want to do?",
        choices=options,
    ).execute()

    if choice == "Add a Device":
        site = get_or_create_site()

        device_types = get_device_types()
        device_roles = get_device_roles()
        display_device_types_and_roles(device_types, device_roles)

        while True:
            device_name = Prompt.ask("Enter the device name (format: 3 letter site, Device Role, Device Type and then number)")
            try:
                DeviceNameModel(name=device_name)
                break
            except ValidationError as e:
                console.print(f"[bold red]Error:[/bold red] {e}")

        device_type = Prompt.ask("Enter the device type ID")
        device_role = Prompt.ask("Enter the device role ID")
        tenant = Prompt.ask("Enter the tenant ID (optional)", default=None)

        device = create_device(site.id, device_name, device_type, device_role, tenant)
        console.print(f"[bold green]Created new device:[/bold green] {device.name} (ID: {device.id})")

        display_created_device(device)

if __name__ == "__main__":
    show_menu()