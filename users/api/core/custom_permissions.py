from rest_framework  import permissions
from django.core.cache import cache


class OTPVerifiedPermission(permissions.BasePermission):
    message  = 'the otp has not been verified'

    def has_permission(self, request, view):
        email = request.query_params.get('email')
        if cache.get(f'otp_verified_{email}'):
            return True