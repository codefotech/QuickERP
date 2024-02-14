from librouteros import connect


def process_interface_data(raw_data):
    # Process your raw data here and return the processed data in a suitable format
    # For example, you might convert the data into a list of dictionaries
    processed_data = []

    for entry in raw_data:
        processed_entry = {
            'name': entry.get('name'),
            'type': entry.get('type'),
            'status': entry.get('status')
            # Add more fields as needed
        }
        processed_data.append(processed_entry)

    return processed_data


connection = connect(username='test', password='test', host='103.20.242.22', port='8523')
interface_data = connection('/interface/print')

processed_data = process_interface_data(raw_data=interface_data)

print('router os ',processed_data)





import paramiko

# MikroTik router credentials
router_ip = "103.20.242.22"
username = "test"
password = "test"
port = '8527'

# SSH connection setup
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the router
try:
    ssh_client.connect(router_ip, username=username, password=password, port=port)
    print("Connected to the MikroTik router.")

    # Send commands and receive output
    command = "/interface print"
    stdin, stdout, stderr = ssh_client.exec_command(command)

    # Print the output of the command
    print(stdout.read().decode())

except paramiko.AuthenticationException:
    print("Authentication failed.")
except paramiko.SSHException as e:
    print(f"SSH connection error: {e}")
finally:
    # Close the SSH connection
    ssh_client.close()
