import requests
import time
import json

# Base config
base_url = "http://192.168.1.159:30080"
auth_url = f"{base_url}/api/v2/tokens/"
launch_url = f"{base_url}/api/v2/job_templates/20/launch/"

username = "admin"
password = "KanKu009"

# Get the token
response = requests.post(auth_url, auth=(username, password))
if response.status_code != 201:
    print("❌ Failed to get token")
    exit()

token = response.json()["token"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 👇 Ask user for hostname
interface_ip = input("Enter the Interface IP: ")
interface_description = input("Enter the Interface Description: ")

# 👇 Inject hostname into extra_vars
extra_vars = {
    "interface_ip": interface_ip,
    "interface_description": interface_description 
}
payload = {
    "extra_vars": json.dumps(extra_vars)  # Convert extra_vars to a JSON-formatted string
}

# Print the vars being passed
print("Sending extra_vars to AWX")
print(payload)

# Launch the job with extra_vars
launch_response = requests.post(launch_url, headers=headers, json=payload)
if launch_response.status_code not in (201, 202):
    print("❌ Failed to launch job")
    print(launch_response.text)
    exit()

job_id = launch_response.json()["id"]
job_url = f"{base_url}/api/v2/jobs/{job_id}/"

job_info = requests.get(job_url, headers=headers).json()
print("✅ AWX received these extra_vars:")
print(job_info.get("extra_vars"))

job_id = launch_response.json()["id"]
print(f"🚀 Job {job_id} launched with IP: {interface_ip}")

# Poll job status
job_url = f"{base_url}/api/v2/jobs/{job_id}/"
stdout_url = f"{job_url}stdout/?format=txt"

print("🔁 Waiting for job to finish...")

while True:
    job_response = requests.get(job_url, headers=headers).json()
    status = job_response["status"]
    if status in ["successful", "failed", "error", "canceled"]:
        print(f"✅ Job finished with status: {status}")
        break
    print(f"Job status: {status}... waiting")
    time.sleep(2)

# Get stdout
stdout_response = requests.get(stdout_url, headers=headers)
print("\n📜 Job Output:\n")
print(stdout_response.text)
