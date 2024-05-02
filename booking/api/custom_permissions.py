from rest_framework  import permissions


class UserIsDoctor(permissions.BasePermission):
    message = 'permission denied'

    def has_permission(self, request, view):
        return not request.user.category == 'DR'
    

class UserIsPatient(permissions.BasePermission):
    message = 'permission denied'
    
    def has_permission(self, request, view):
        return not request.user.category == 'PT'