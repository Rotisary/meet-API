from rest_framework.views import exception_handler
from rest_framework.pagination import PageNumberPagination
from rest_framework.schemas.openapi import SchemaGenerator


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status code'] = response.status_code
        response.data['status text'] = response.status_text

    return response


class CustomPagination(PageNumberPagination):
    page_size = 2


class CustomSchemaGenerator(SchemaGenerator):
    pass
