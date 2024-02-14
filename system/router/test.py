import paramiko


class MikroTikSSHManager:
    _instances = {}

    @classmethod
    def get_instance(cls, router_ip, username, password, port=22):
        router_key = (router_ip, username, password, port)
        if router_key not in cls._instances:
            cls._instances[router_key] = cls._create_instance(router_ip, username, password, port)
        return cls._instances[router_key]

    @staticmethod
    def _create_instance(router_ip, username, password, port):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(router_ip, port=port, username=username, password=password)
            return ssh_client
        except paramiko.AuthenticationException:
            print(f"Authentication failed for {router_ip}, please check your credentials.")
        except paramiko.BadHostKeyException as badHostKeyException:
            print(f"Unable to verify server's host key for {router_ip}: {badHostKeyException}")
        except paramiko.SSHException as sshException:
            print(f"Unable to establish SSH connection to {router_ip}: {sshException}")
        except Exception as e:
            print(f"Exception: {e}")

def connect_router(router_ip, username, password,port):
    router_instance = MikroTikSSHManager.get_instance(router_ip, username, password, port=port)
    # Now you can use this instance to perform operations on the router
    # For example:
    if router_instance:
        stdin, stdout, stderr = router_instance.exec_command('/ip hotspot user add name=126')
        print(stdout.read().decode())
    else:
        print('Router Exception')
