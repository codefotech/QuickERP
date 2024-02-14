from datetime import datetime, timedelta

import paramiko

from apps.router.models import Router
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class MikroTikSSHManager:
    _instances = {}

    @classmethod
    def get_instance(cls, router_ip, username, password, port=22):
        router_key = (router_ip, username, password, port)
        if router_key not in cls._instances:
            cls.close_instance(router_key)
            connection_instance = cls._create_instance(router_ip, username, password, port)
            if connection_instance:
                cls._instances[router_key] = {
                    'connection': connection_instance
                }
                if cls._instances[router_key]['connection']:
                    cls._instances[router_key]['timeout'] = datetime.now() + timedelta(minutes=30)
        elif cls._instances[router_key]['connection'] and cls._instances[router_key]['timeout'] < datetime.now():
            cls.close_instance(router_key)
            connection_instance = cls._create_instance(router_ip, username, password, port)
            if connection_instance:
                cls._instances[router_key] = {
                    'connection': connection_instance
                }
                if cls._instances[router_key]['connection']:
                    cls._instances[router_key]['timeout'] = datetime.now() + timedelta(minutes=30)

        if cls._instances.get(router_key):
            return cls._instances[router_key]['connection']
        else:
            return None

    @staticmethod
    def _create_instance(router_ip, username, password, port):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(router_ip, port=port, username=username, password=password, timeout=5,
                               look_for_keys=False)
            return ssh_client
        except paramiko.AuthenticationException:
            print(f"Authentication failed for {router_ip}, please check your credentials.")
            return False
        except paramiko.BadHostKeyException as badHostKeyException:
            print(f"Unable to verify server's host key for {router_ip}: {badHostKeyException}")
            return False
        except paramiko.SSHException as sshException:
            print(f"Unable to establish SSH connection to {router_ip}: {sshException}")
            return False
        except Exception as e:
            print(f"Exception: {e}")
            return False

    @staticmethod
    def connect_router(router_ip, username, password, port):
        if router_ip and username and password and port:
            router_instance = MikroTikSSHManager.get_instance(router_ip, username, password, port=port)
        else:
            router_instance = False
        return router_instance

    @classmethod
    def close_instance(cls, router_key):
        if router_key in cls._instances:
            instance = cls._instances.pop(router_key)
            instance['connection'].close()


def add_pppoe_user(router_id, profile, username, password):
    try:
        router = Router.objects.get(id=router_id)
        connection = MikroTikSSHManager.connect_router(router.ip_address, router.user_name,
                                                       router.password,
                                                       router.api_port)
        connection.exec_command(f'ppp secret add name={username} password={password} profile={profile} service=pppoe')
        logger.warning('PPPOE User added at ' + str(datetime.now()) + ' hours!')

        return "User added successfully"  # You can customize the success message
    except Exception as e:
        return f"Error: {str(e)}"  # Return an error message with the exception details
