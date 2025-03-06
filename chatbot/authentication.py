from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Partner

class PartnerAPIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('Authorization')

        if not api_key:
            return None

        try:
            partner = Partner.objects.get(api_key=api_key)
        except Partner.DoesNotExist:
            raise AuthenticationFailed("Invalid API Key")

        return (partner, None)