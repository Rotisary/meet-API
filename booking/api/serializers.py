import datetime
from rest_framework import serializers
from booking.models import Complaint, Meet, Appointment, Symptom
from users.api.serializers import ProfileSerializer
from users.models import Profile
from booking.api.utils.ext_api_helpers import filter_doctors


class ComplaintSerializer(serializers.HyperlinkedModelSerializer):
    meet = serializers.HyperlinkedRelatedField(
        view_name = 'meet-detail',
        read_only = True,
        lookup_field='ID'  
    )
    class Meta:
        model = Complaint
        fields = ['id', 'url', 'symptom', 'sex', 'year_of_birth', 'age_group', 'patient', 'treated_by', 'meet']
        extra_kwargs = {
            'patient': {
                'lookup_field': 'username',
                'read_only': True
            },
            'id': {
                'read_only': True
            },
            'treated_by': {
                'lookup_field': 'slug',
                'read_only': True
            }
        }

    
    def validate_year_of_birth(self, value):
        if len(str(abs(value))) != 4:
            raise serializers.ValidationError({'error': 'year cannot be more than four digits'})
        elif value > datetime.datetime.now().year:
            raise serializers.ValidationError({'error': 'year is invalid'})
        return value
    

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        request = self.context["request"]
        data = filter_doctors(instance, Profile, ProfileSerializer, request)
        obj = instance.save()
        return data, obj


    def create(self, validated_data):
        return Complaint.objects.create(**validated_data)
    


class MeetSerializer(serializers.HyperlinkedModelSerializer):
    patient = serializers.SerializerMethodField('get_patient_name')
    class Meta:
        model = Meet
        fields = ['url', 'ID', 'doctor', 'patient', 'complaint']
        extra_kwargs = {
            'url': {'lookup_field': 'ID'},
            'ID': {'read_only': True},
            'doctor': {
                'view_name': 'profile-detail',
                'lookup_field': 'slug',
                'read_only': True
            },
            'complaint': {
                'view_name': 'complaint-detail',
                'read_only': True
            }
        }


    def get_patient_name(self, obj):
        first_name = obj.patient.first_name
        last_name = obj.patient.last_name
        full_name = f"{first_name} {last_name}"
        return full_name
    

class SymptomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Symptom
        fields = ['ID', 'Name']
        extra_kwargs = {
            'ID': {'read_only': True},
            'Name': {'read_only': True}
        }


class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    patient = serializers.SerializerMethodField('get_patient_name')

    class Meta:
        model = Appointment
        fields = ['id', 'url', 'owner', 'patient', 'date_of_appointment', 'time_of_appointment']
        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'owner': {
                'view_name': 'profile-detail',
                'lookup_field': 'slug',
                'read_only': True
            },
        }

    
    def validate_date_of_appointment(self, value):
        if value < datetime.date.today():
            raise serializers.ValidationError({'error': 'enter valid date'})
        return value
    

    def validate(self, data):
        date_of_appointment = data.get('date_of_appointment')
        time_of_appointment = data.get('time_of_appointment')

        now = datetime.datetime.now()

        if date_of_appointment == now.date() and time_of_appointment <= now.time():
            raise serializers.ValidationError({'error': 'Enter a valid time.'})

        return data

   
    def get_patient_name(self, appointment):
        first_name = appointment.patient.first_name
        last_name = appointment.patient.last_name
        full_name = f"{first_name} {last_name}"
        return full_name
    
    def create(self, validated_data):
        return Appointment.objects.create(**validated_data)
    

    def update(self, instance, validated_data):
        instance.owner = validated_data.get('owner', instance.owner)
        instance.patient = validated_data.get('patient', instance.patient)
        instance.date_of_appointment = validated_data.get('date_of_appointment', instance.date_of_appointment)
        instance.time_of_appointment = validated_data.get('time_of_appointment', instance.time_of_appointment)
        instance.save()
        return instance