

class UnavailableRouterError(Exception):
    def __init__(self, message="This router is not available"):
        self.message = message
        super().__init__(self.message)