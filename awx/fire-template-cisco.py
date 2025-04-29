from rich.console import Console
from rich.table import Table
from rich.prompt import IntPrompt
import requests
import time
import json

# Instantiate a Rich Console
console = Console()

# Base config
base_url = "http://192.168.1.159:30080"
auth_url = f"{base_url}/api/v2/tokens/"
job_templates_url = f"{base_url}/api/v2/job_templates/"

username = "admin"
password = "KanKu009"

# Authenticate and get token
console.rule("[bold blue]Authenticating with AWX")
response = requests.post(auth_url, auth=(username, password))
if response.status_code != 201:
    console.print(":x: [bold red]Failed to get token[/bold red]")
    exit()

token = response.json()["token"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

console.print(":white_check_mark: [bold green]Token received successfully![/bold green]")

# Fetch job templates
console.rule("[bold blue]Fetching Job Templates")
templates_response = requests.get(job_templates_url, headers=headers)
if templates_response.status_code != 200:
    console.print(":x: [bold red]Failed to fetch job templates[/bold red]")
    exit()

job_templates = templates_response.json()["results"]

if not job_templates:
    console.print(":x: [bold red]No job templates found[/bold red]")
    exit()

# Display job templates in a table
table = Table(title="Available Job Templates", show_lines=True)
table.add_column("ID", justify="center", style="cyan", no_wrap=True)
table.add_column("Name", justify="left", style="magenta")
table.add_column("Description", justify="left", style="green")

for template in job_templates:
    table.add_row(str(template["id"]), template["name"], template.get("description", "No description available"))

console.print(table)

# Prompt user to select a job template
job_template_id = IntPrompt.ask("[bold yellow]Enter the ID of the job template you want to launch[/bold yellow]")
selected_template = next((template for template in job_templates if template["id"] == job_template_id), None)

if not selected_template:
    console.print(":x: [bold red]Invalid job template ID selected[/bold red]")
    exit()

console.print(f":rocket: [bold green]Selected Job Template: {selected_template['name']}[/bold green]")

# Prompt user for extra_vars
console.rule("[bold blue]Enter Job Variables")
hostname = console.input("\n[bold green]Enter the Hostname: [/bold green]\n")  # Added line spacing
interface_description = console.input("\n[bold green]Enter the Interface Description: [/bold green]\n")  # Added line spacing
interface_ip = console.input("[green]Enter the interface IP: [/green]")
subnet_mask = console.input("[green]Enter the subnet mask: [/green]")
enable_password = console.input("[green]Enbable Password:(e.g. Gig0/1): [/green]")

# Prepare extra_vars and payload
extra_vars = {
    "hostname": hostname,
    "interface_description": interface_description,
    "interface_ip": interface_ip,
    "subnet_mask": subnet_mask,
    "enable_password": enable_password
}
payload = {
    "extra_vars": json.dumps(extra_vars)  # Convert to JSON string
}

# Launch the selected job template
launch_url = f"{base_url}/api/v2/job_templates/{job_template_id}/launch/"
console.rule("[bold blue]Launching AWX Job")
console.print("[bold yellow]Sending extra_vars to AWX:[/bold yellow]")
console.print(payload)

launch_response = requests.post(launch_url, headers=headers, json=payload)
if launch_response.status_code not in (201, 202):
    console.print(":x: [bold red]Failed to launch job[/bold red]")
    console.print(launch_response.text)
    exit()

job_id = launch_response.json().get("id")
if not job_id:
    console.print(":x: [bold red]Unable to retrieve job ID from response[/bold red]")
    console.print(launch_response.json())
    exit()

console.print(f":rocket: [bold green]Job {job_id} Launched")

# Poll job status
job_url = f"{base_url}/api/v2/jobs/{job_id}/"
stdout_url = f"{job_url}stdout/?format=txt"

console.rule("[bold blue]Polling Job Status")
with console.status("[cyan]Waiting for job to complete...[/cyan]") as status:
    while True:
        job_response = requests.get(job_url, headers=headers).json()
        status_text = job_response["status"]
        if status_text in ["successful", "failed", "error", "canceled"]:
            console.print(f":white_check_mark: [bold green]Job finished with status: {status_text}[/bold green]" if status_text == "successful" else f":x: [bold red]Job finished with status: {status_text}[/bold red]")
            break
        time.sleep(2)

# Get stdout
console.rule("[bold blue]Retrieving Job Output")
stdout_response = requests.get(stdout_url, headers=headers)
console.print("\n[bold yellow]Job Output:[/bold yellow]\n")
console.print(stdout_response.text)