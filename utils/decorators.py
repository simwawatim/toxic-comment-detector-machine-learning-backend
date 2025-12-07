from functools import wraps
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from utils.response import api_response

def jwt_required(func):
    @wraps(func)
    def wrapper(view, request, *args, **kwargs):
        jwt_auth = JWTAuthentication()
        try:
            user_auth_tuple = jwt_auth.authenticate(request)
            if user_auth_tuple is None:
                return api_response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    status='fail',
                    message='Authentication credentials were not provided or invalid.'
                )
            request.user, _ = user_auth_tuple
        except AuthenticationFailed as e:
            return api_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                status='fail',
                message=str(e)
            )
        return func(view, request, *args, **kwargs)
    return wrapper
