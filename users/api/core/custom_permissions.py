from rest_framework  import permissions
from django.core.cache import cache


class OTPVerifiedPermission(permissions.BasePermission):
    message  = 'user verification failed. Try again'

    def has_permission(self, request, view):
        email = request.query_params.get('email')
        if cache.get(f'otp_verified_{email}'):
            return True


class UserIsPatient(permissions.BasePermission):
    message = 'permission denied'

    def has_permission(self, request, view):
        return not request.user.category == 'DR'
    

class UserIsDoctor(permissions.BasePermission):
    message = 'permission denied'
    
    def has_permission(self, request, view):
        return not request.user.category == 'PT'

    
class ReviewDetailPerm(permissions.BasePermission):
        
    def has_object_permission(self, request, view, obj):
        return request.user.category == 'PT' or request.user == obj.doctor.user 
