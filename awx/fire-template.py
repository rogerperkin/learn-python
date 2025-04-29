import requests

# Replace with your actual API URL
url = "http://192.168.1.159:30080/api/v2/job_templates/21/launch/"

# If authentication is required, use the appropriate method
# Example: Bearer token
headers = {
    "Authorization": "ZEThYV4L12GmAlCPgxmXnTfBTC3VeL",  # Replace with your actual token
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Optional: If you need to send extra data with the launch
payload = {
    # Example: "extra_vars": {"key": "value"}
}

try:
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201 or response.status_code == 202:
        print("Job launched successfully!")
        print("Response:", response.json())
    else:
        print(f"Failed to launch job. Status code: {response.status_code}")
        print("Response:", response.text)

except requests.exceptions.RequestException as e:
    print("An error occurred:", e)
