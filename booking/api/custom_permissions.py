from rest_framework  import permissions
from rest_framework.filters import SearchFilter
from users.models import User
from rest_framework.metadata import SimpleMetadata


class UserIsPatient(permissions.BasePermission):
    message = 'permission denied'

    def has_permission(self, request, view):
        return not request.user.category == 'DR'
    

class UserIsDoctor(permissions.BasePermission):
    message = 'permission denied'
    
    def has_permission(self, request, view):
        return not request.user.category == 'PT'
    

class ComplaintDetailPerm(permissions.BasePermission):
        
    def has_object_permission(self, request, view, obj):
        if request.user.category == 'PT':
            return request.user == obj.patient
        else:
            return request.user.profile in obj.patient.meets.all()
        

class AppointmentDetailPerm(permissions.BasePermission):
        
    def has_object_permission(self, request, view, obj):
        return request.user == obj.patient or request.user.profile == obj.owner 
        

class ReviewDetailPerm(permissions.BasePermission):
        
    def has_object_permission(self, request, view, obj):
        return request.user.category == 'PT' or request.user == obj.doctor.user 


class DoctorsComplaintPerm(permissions.BasePermission):
    message = 'bad request'
    
    def has_permission(self, request, view):
        username = request.query_params.get('username')
        user = User.objects.get(username=username)
        return not user.category == 'PT'
    

# class CustomSimpleMetadata(SimpleMetadata):

#     def determine_metadata(self, request, view):
#         return {
#             'name': view.get_view_name(),
#             'description': view.get_view_description()
#         }
