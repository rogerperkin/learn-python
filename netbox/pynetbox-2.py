import pynetbox
import ipaddress
import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

# NetBox API URL and Token
NETBOX_API_URL = "http://localhost:8000"  # Replace with your NetBox instance URL
API_TOKEN = "3f8908181dcc5ede256e8610b8b374adcb43b457"  # Replace with your NetBox API token

# Initialize pynetbox connection
netbox = pynetbox.api(NETBOX_API_URL, token=API_TOKEN)

# Initialize Rich Console for pretty output
console = Console()

# Function to get all parent prefixes from NetBox (only top-level prefixes)
def get_all_parent_prefixes():
    # Fetch all prefixes from NetBox
    prefixes = netbox.ipam.prefixes.all()

    # Filter out only the top-level parent prefixes (e.g., /16, /8) 
    parent_prefixes = []
    for prefix in prefixes:
        # Convert the prefix to an ipaddress.IPv4Network object
        network = ipaddress.IPv4Network(prefix['prefix'])

        # Check if the prefix is a top-level prefix by ensuring no other prefix contains it
        is_top_level = True
        for other_prefix in prefixes:
            other_network = ipaddress.IPv4Network(other_prefix['prefix'])
            if other_network != network and network.subnet_of(other_network):
                # If the prefix is a subnet of another prefix, it is not a top-level prefix
                is_top_level = False
                break
        
        # Add to the list if it's a top-level parent prefix
        if is_top_level:
            parent_prefixes.append(prefix)
    
    return parent_prefixes

# Function to find the next available /31 subnet within the parent prefix
def get_next_available_subnet(parent_prefix):
    # Convert the parent prefix to an ipaddress.IPv4Network object
    parent_network = ipaddress.IPv4Network(parent_prefix)

    # Iterate through possible /31 subnets within the parent prefix
    for subnet in parent_network.subnets(new_prefix=31):
        # Check if this subnet is already used in NetBox
        if not is_prefix_in_netbox(str(subnet)):
            return subnet

    return None

# Function to check if a subnet is already used in NetBox
def is_prefix_in_netbox(subnet):
    # Query NetBox for existing prefixes
    prefixes = netbox.ipam.prefixes.filter(prefix=subnet)

    # If the prefix is found in NetBox, it's already in use
    return any(p['prefix'] == subnet for p in prefixes)

# Function to get the next 2 usable IPs from a /31 subnet
def get_usable_ips_from_subnet(subnet):
    # Convert subnet to an ipaddress.IPv4Network object
    network = ipaddress.IPv4Network(subnet)

    # Ensure it's a /31 subnet
    if network.prefixlen != 31:
        console.print(f"The subnet [bold red]{subnet}[/bold red] is not a /31 subnet.", style="bold red")
        return []

    # Get the usable IPs in the /31 range (only 2 usable IPs in a /31)
    usable_ips = list(network.hosts())[:2]  # Only take the first 2 usable IPs
    return usable_ips

# Function to provision a new /31 subnet into NetBox
def provision_new_subnet(parent_prefix, subnet, description):
    # Create a new prefix (subnet) in NetBox
    data = {
        "prefix": str(subnet),
        "tenant": None,  # Adjust if you need to assign it to a tenant
        "description": description,  # Use the provided description
    }

    # Make the API request to create the new prefix
    netbox.ipam.prefixes.create(**data)
    console.print(f"Successfully provisioned new /31 subnet: {subnet} with description: [bold green]{description}[/bold green]", style="bold green")

# Example usage
if __name__ == "__main__":
    # Fetch and display all parent prefixes configured in NetBox
    console.print("[bold blue]Fetching all top-level parent prefixes from NetBox...[/bold blue]\n")
    parent_prefixes = get_all_parent_prefixes()

    if not parent_prefixes:
        console.print("[bold red]No top-level parent prefixes found in NetBox.[/bold red]")
        sys.exit(1)

    # Display the available parent prefixes to the user in a table format
    table = Table(title="Available Parent Prefixes")
    table.add_column("No.", justify="right", style="cyan", no_wrap=True)
    table.add_column("Parent Prefix", style="magenta")

    for idx, prefix in enumerate(parent_prefixes, 1):
        table.add_row(str(idx), prefix['prefix'])

    console.print(table)

    # Prompt the user to select a parent prefix
    try:
        choice = Prompt.ask("\n[bold cyan]Enter the number of the parent prefix to select:[/bold cyan]", console=console, default="1")
        choice = int(choice)
        if 1 <= choice <= len(parent_prefixes):
            selected_prefix = parent_prefixes[choice - 1]['prefix']
            console.print(f"\nYou selected: [bold green]{selected_prefix}[/bold green]")
        else:
            console.print("[bold red]Invalid choice, exiting.[/bold red]")
            sys.exit(1)
    except ValueError:
        console.print("[bold red]Invalid input, please enter a valid number.[/bold red]")
        sys.exit(1)

    # Ask the user if they want to request a new /31 subnet
    request_new = Prompt.ask(f"\n[bold cyan]Do you want to request a new /31 subnet within {selected_prefix}? (yes/no)[/bold cyan]", console=console, default="yes").strip().lower()

    if request_new != "yes":
        console.print("[bold yellow]Exiting without provisioning a new subnet.[/bold yellow]")
        sys.exit(0)

    # Get the next available /31 subnet within the selected parent prefix
    next_available_subnet = get_next_available_subnet(selected_prefix)

    if next_available_subnet:
        console.print(f"\n[bold blue]Next available /31 subnet: {next_available_subnet}[/bold blue]")
        
        # Ask for a description for the new /31 subnet
        description = Prompt.ask(f"[bold cyan]Enter a description for the new /31 subnet {next_available_subnet}[/bold cyan]:", console=console).strip()

        # Provision this new /31 subnet in NetBox
        provision_new_subnet(selected_prefix, next_available_subnet, description)
        
        # Get the 2 usable IPs from the found /31 subnet
        usable_ips = get_usable_ips_from_subnet(next_available_subnet)
        
        if usable_ips:
            console.print("\n[bold green]Next 2 usable IPs in the /31 range:[/bold green]")
            for ip in usable_ips:
                console.print(f"  [bold magenta]{ip}[/bold magenta]")
    else:
        console.print(f"[bold red]No available /31 subnets found within {selected_prefix}.[/bold red]")