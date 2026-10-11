from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Standardizes error responses across all DRF views.
    Ensures that validation errors, authentication failures, and not found
    exceptions are returned with a consistent error structure:
    {"error": ...}
    """
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(response.data, dict):
            if "error" not in response.data:
                response.data = {"error": response.data}
        elif isinstance(response.data, list):
            response.data = {"error": response.data}

    return response
