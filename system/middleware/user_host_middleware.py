from system.config import _thread_local

class UserHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the user's host address from the request
        user_host = request.META.get('HTTP_HOST')

        # Set the user host address in the thread-local variable
        _thread_local.request = request
        _thread_local.user_host = user_host
        _thread_local.user_type_parts_first = None
        if request.user:
            _thread_local.user = request.user
            _thread_local.session = request.session
        if hasattr(request.user, 'user_type'):
            user_type = request.user.user_type
            user_type_parts_first = user_type.split('x')[0]
            _thread_local.user_type_parts_first = user_type_parts_first

        response = self.get_response(request)

        return response


class XFrameOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Frame-Options'] = 'ALLOW-FROM http://103.20.242.22:8080'
        return response