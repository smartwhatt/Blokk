from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTBackend:
    authenticator = JWTAuthentication()

    def authenticate(self, request=None, **kwargs):
        if request is None:
            return None

        # calls restful jwt auth
        tuple_user = self.authenticator.authenticate(request)

        if type(tuple_user) is tuple:
            return tuple_user[0]

        return None