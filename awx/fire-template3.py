from rich.console import Console
from rich.progress import Progress
import requests
import time
import json

# Instantiate a Rich Console
console = Console()

# Base config
base_url = "http://192.168.1.159:30080"
auth_url = f"{base_url}/api/v2/tokens/"
launch_url = f"{base_url}/api/v2/job_templates/20/launch/"

username = "admin"
password = "KanKu009"

# Get the token
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

# Prompt user for input
console.rule("[bold blue]Enter Job Variables")
interface_ip = console.input("\n[bold green]Enter the Interface IP: [/bold green]\n")  # Added line spacing
interface_description = console.input("\n[bold green]Enter the Interface Description: [/bold green]\n")  # Added line spacing

# Prepare extra_vars and payload
extra_vars = {
    "interface_ip": interface_ip,
    "interface_description": interface_description 
}
payload = {
    "extra_vars": json.dumps(extra_vars)  # Convert to JSON string
}

console.rule("[bold blue]Launching AWX Job")
console.print("[bold yellow]Sending extra_vars to AWX:[/bold yellow]")
console.print(payload)

# Launch the job with extra_vars
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

console.print(f":rocket: [bold green]Job {job_id} Launched ")

# Poll job status
job_url = f"{base_url}/api/v2/jobs/{job_id}/"
stdout_url = f"{job_url}stdout/?format=txt"

console.rule("[bold blue]Polling Job Status")
with Progress() as progress:
    task = progress.add_task("[cyan]Waiting for job to finish...", total=None)
    while True:
        job_response = requests.get(job_url, headers=headers).json()
        status = job_response["status"]
        if status in ["successful", "failed", "error", "canceled"]:
            progress.stop()
            console.print(f":white_check_mark: [bold green]Job finished with status: {status}[/bold green]" if status == "successful" else f":x: [bold red]Job finished with status: {status}[/bold red]")
            break
        progress.refresh()
        time.sleep(2)

# Get stdout
console.rule("[bold blue]Retrieving Job Output")
stdout_response = requests.get(stdout_url, headers=headers)
console.print("\n[bold yellow]📜 Job Output:[/bold yellow]\n")
console.print(stdout_response.text)