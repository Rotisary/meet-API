from rest_framework  import permissions
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import ValidationError
from users.models import User
from rest_framework.metadata import SimpleMetadata
    

class ComplaintPerm(permissions.BasePermission):

    def has_permission(self, request, view):
        username = request.query_params.get('username')
        if not username:
            raise ValidationError('error. Please add the username of the patient')
        else:
            user = User.objects.get(username=username)
            return user.meets_booked.filter(has_ended=False, doctor=request.user.profile).exists()
        
        
    def has_object_permission(self, request, view, obj):
        if request.user.category == 'PT':
            return request.user == obj.patient
        else:
            user = obj.patient
            return user.meets_booked.filter(has_ended=False, doctor=request.user.profile).exists()
        

class MeetDetailPerm(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.patient or request.user == obj.doctor.user
        

class AppointmentDetailPerm(permissions.BasePermission):
        
    def has_object_permission(self, request, view, obj):
        return request.user == obj.patient or request.user.profile == obj.owner 
        

class DoctorsComplaintPerm(permissions.BasePermission):
    message = 'bad request'
    
    def has_permission(self, request, view):
        username = request.query_params.get('username')
        user = User.objects.get(username=username)
        return not user.category == 'PT'
    

class ComplaintUpdatePerm(permissions.BasePermission):
    message = 'you cannot update this complaint'

    def has_object_permission(self, request, view, obj):
        return obj.treated_by == None
