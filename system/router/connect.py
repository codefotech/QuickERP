from librouteros import connect
import paramiko


class MikroTikManager:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        ip = kwargs.get('ip')
        port = kwargs.get('port')
        username = kwargs.get('username')
        password = kwargs.get('password')

        # Creating a key using a tuple of the provided parameters
        key = (ip, port, username, password)

        if key not in cls._instances:
            cls._instances[key] = super(MikroTikManager, cls).__new__(cls)

        return cls._instances[key]

    def __init__(self, ip, username, password, port=None):
        if not hasattr(self, 'initialized'):
            self.ip = ip
            self.port = port
            self.username = username
            self.password = password
            self.connection = None
            self.initialized = True

    def connect(self):
        try:
            if not self.connection:
                self.connection = connect(
                    host=self.ip,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                )

                return self.connection
            else:
                return self.connection
        except Exception as e:
            return False

            # You can log the error, display a message, or take other appropriate actions

    def print_interfaces(self):
        if self.connection:
            print(f"Interfaces on {self.ip} ({self.port}):")
            # Use the cmd method to send commands
            # interfaces = self.connection.cmd('/interface/print')
            # for resource in interfaces:
            #     print(resource)
        else:
            print("Not connected.")
