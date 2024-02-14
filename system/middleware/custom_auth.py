from django.shortcuts import redirect
from system.config import GlobalConfig
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import resolve
from django.conf import settings


class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.media_url = getattr(settings, 'MEDIA_URL', '/media/')

    def __call__(self, request):
        # Check if the user is authenticated

        no_auth_url_list = GlobalConfig.no_auth_url_list()

        if request.user.is_authenticated and not request.user.is_anonymous:
            response = self.get_response(request)
            if request.session.get('logged_in_pass'):
                return response
            else:
                if not request.user.is_anonymous:
                    if request.user.auth_token_allow == 1 and request.user.auth_token != '':
                        if request.path not in no_auth_url_list:
                            logout(request)
                            messages.error(request, '2nd Step verification not match properly. Please login again.')
                            return redirect('login')
                else:
                    logout(request)
                    return redirect('login')

        elif request.path.startswith(self.media_url):
            return self.get_response(request)
        else:
            url = resolve(request.path)
            # User is not authenticated, check if the requested URL is the login URL
            if url.url_name in no_auth_url_list or 'api' in request.path:
                # The requested URL is the login URL, pass the request on to the next middleware

                response = self.get_response(request)

            else:
                # Redirect the user to the login page
                response = redirect('login')

        return response
