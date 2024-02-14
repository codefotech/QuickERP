from librouteros import connect
import paramiko
import subprocess

from apps.hotspot_router.models import HotspotRouter
from apps.router.models import Router
import logging
import socket

logger = logging.getLogger(__name__)


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


def check_router_status(id=None):
    if id:
        router = Router.objects.get(id=id)
        return is_router_port_active(router.ip_address, router.ssh_port)
        # try:
        #     result = subprocess.run(['ping', '-c', '4', router.ip_address], capture_output=True, text=True, timeout=10)
        #     if result.returncode == 0:
        #         return True
        #     else:
        #         return False
        #
        # except subprocess.TimeoutExpired:
        #     logger.error('This is an error message.[(issue.apps-router.router_os.routing)-Issue-102]')
        #     return False
        #
        # except Exception as e:
        #     return f"Exception[(issue.apps-router.router_os.routing)-Issue-103]: {str(e)}"


def is_router_port_active(router_ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        result = sock.connect_ex((router_ip, int(port)))

        if result == 0:
            return True
        else:
            return False

    except Exception as e:
        logger.error(f'Error.[(issue.apps-router.router_os.routing)-Issue-102]: {str(e)}')
        return False


def check_router_connection(router_ip, username, password, port):
    connection = None  # Initialize the variable

    try:
        # Connect to the MikroTik router API
        connection = connect(host=router_ip, username=username, password=password, port=port)

        # Execute a command to check connectivity (you can use any API command here)
        response = connection(cmd='/ping', address='8.8.8.8', count='3')

        # Check the response for successful ping
        if response:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Close the API connection if it was successfully opened
        if connection:
            connection.close()
