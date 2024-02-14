# custom middleware to bypass authentication for media URLs
from django.conf import settings
from django.http import HttpResponseForbidden


class MediaAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.media_url = getattr(settings, 'MEDIA_URL', '/media/')

    def __call__(self, request):
        # Check if the requested URL starts with the media URL
        if request.path.startswith(self.media_url):
            # Allow access to media URLs without authentication
            return self.get_response(request)

        # For other URLs, perform authentication checks
        # Your authentication logic goes here

        return self.get_response(request)
