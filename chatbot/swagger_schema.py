from drf_yasg import openapi


api_key_header = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="API Key for Partner (Authorization API)",
    type=openapi.TYPE_STRING
)
