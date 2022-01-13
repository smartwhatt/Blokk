import logging

from django.contrib.auth import authenticate


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        logging.info("JWTAuthMiddleware called")
        # authenticate user
        try:
            user = authenticate(request)
            if user is not None and user.is_authenticated:
                logging.info("JWTAuthMiddleware user set " + str(user))
                request.user = user
        except Exception as err:
            logging.info("JWTAuthMiddleware failed " + str(err))

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response