from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework import status
from utils.response import api_response

def custom_exception_handler(exc, context):
    if isinstance(exc, (TokenError, InvalidToken)):
        if hasattr(exc, 'args') and len(exc.args) > 0 and isinstance(exc.args[0], dict):
            detail = exc.args[0]
            message = {k: str(v) for k, v in detail.items()}
        else:
            message = str(exc)

        return api_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            status='fail',
            message=message
        )
    return exception_handler(exc, context)
