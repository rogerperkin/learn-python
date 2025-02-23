import requests

# NetBox API URL and token
api_url = 'http://192.168.1.182:8050/api'
token = '200bfa1b4174533f59417854e9dafb3add08'

# Headers for authentication
headers = {
    'Authorization': f'Token {token}'
}

# Define the subnet (example subnet)
subnet = '192.168.1.0/24'

# Step 1: Get Prefix (Subnet) details
response = requests.get(f'{api_url}/ipam/prefixes/', headers=headers, params={'prefix': subnet})
prefixes = response.json()

# Ensure we got a valid response
if prefixes['count'] > 0:
    # Get the prefix ID (if needed for subsequent API calls)
    prefix_id = prefixes['results'][0]['id']
    print(f"Prefix ID: {prefix_id}")
else:
    print("Subnet not found!")

# Step 2: Get all IP addresses in the subnet
response = requests.get(f'{api_url}/ipam/ip-addresses/', headers=headers, params={'network': subnet})
ip_addresses = response.json()

# Step 3: Sort the allocated IP addresses
allocated_ips = [ip['address'] for ip in ip_addresses['results']]
allocated_ips.sort()

# Step 4: Find the next available IP
def next_ip(allocated_ips):
    # Convert the last IP to an integer and add 1
    last_ip = allocated_ips[-1]
    octets = last_ip.split('.')
    octets[-1] = str(int(octets[-1]) + 1)
    return '.'.join(octets)

next_available_ip = next_ip(allocated_ips)
print(f"The next available IP address is: {next_available_ip}")
