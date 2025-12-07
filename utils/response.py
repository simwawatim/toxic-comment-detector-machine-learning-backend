from rest_framework.response import Response

def api_response(status_code=200, status='success', message='', data=None, is_error=False):

    if is_error and isinstance(data, dict):
        messages = []
        for key, value in data.items():
            if isinstance(value, list):
                messages.append(f"{key}: {value[0]}")
            else:
                messages.append(f"{key}: {value}")
        message = " | ".join(messages)
        data = None  

    response = {
        'status_code': status_code,
        'status': status,
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return Response(response, status=status_code)
