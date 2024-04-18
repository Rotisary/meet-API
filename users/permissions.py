from rest_framework import permissions


class  UserNotOwner(permissions.BasePermission):
    message = "you don't have access to this profile"
    def has_object_permissions(self, request, view, obj):
        if obj.user == request.user:
            return True
        else:
            return False

