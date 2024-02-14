import socket
import librouteros
from librouteros.login import plain
from system.Exception.router import UnavailableRouterError

class Microtik:
    @staticmethod
    def connect(router_ip=None, router_port=None, router_username=None, router_password=None):
        if router_ip:
            if router_port:
                if router_username:
                    if router_password:
                        if Microtik.router_ping(router_ip=router_ip, router_port=router_port):
                            try:
                                connection = librouteros.connect(
                                    host=router_ip,
                                    port=router_port,
                                    username=router_username,
                                    password=router_password,
                                    login_methods=plain
                                )
                                return connection
                            except librouteros.exceptions.LibRouterosError as e:
                                raise Exception(f"RouterOS API Error: {e}")
                            except Exception as e:
                                raise Exception(f"Error: {e}")
                        else:
                            raise UnavailableRouterError()

                    else:
                        raise Exception('Router password is missing')
                else:
                    raise Exception('Router username is missing')
            else:
                raise Exception('Router port is missing')
        else:
            raise Exception('Router ip is missing')


    def router_ping(router_ip=None, router_port=None):
        try:
            # Create a socket object
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)  # Set a timeout for the connection attempt (in seconds)

            # Attempt to connect to the router's IP address and port
            result = sock.connect_ex((router_ip, int(router_port)))

            # Check the result code
            if result == 0:
                print(f"The router at {router_ip} is active on port {router_port}")
                return True
            else:
                print(f"The router at {router_ip} is not active on port {router_port}")
                return False

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False
