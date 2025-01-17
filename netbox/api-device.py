import requests
from rich.console import Console
from rich.table import Table

def main():
    """
    Connect to NetBox and retrieve a list of devices, displaying them in a table format.
    """
    url = "http://localhost:8000/api/dcim/devices/"
    token = "219f245258455564c09fe9323f5e38508665a98e"

    # Headers to pass the API token for authentication
    headers = {
        "Accept": "application/json",
        "Authorization": f"Token {token}",
    }

    # Send GET request to the NetBox API
    response = requests.get(url, headers=headers, verify=False)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Check if we have devices in the response
        devices = data.get("results", [])
        if devices:
            # Initialize a rich console
            console = Console()

            # Create a table to display device data
            table = Table(title="Devices List", show_header=True, header_style="bold red")
            table.add_column("Device Name", style="cyan", width=30)
            table.add_column("Device Type", style="cyan", width=30)
            table.add_column("Site", style="green", width=20)

            # Add rows to the table
            for device in devices:
                table.add_row(
                    device["name"], 
                    device["device_type"]["model"], 
                    device["site"]["name"]
                )

            # Print the table to the console
            console.print(table)
        else:
            print("No devices found.")
    else:
        print(f"Failed to fetch devices. HTTP Status Code: {response.status_code}")
        print("Response:", response.text)

if __name__ == "__main__":
    main()
