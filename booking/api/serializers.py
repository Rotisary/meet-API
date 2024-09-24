import datetime
from rest_framework import serializers
from booking.models import Complaint, Appointment, Symptom

# more validations; validation for Complaint update and delete
# update; if they leave a field empty, it should show a message, if they enter a wrong field, it should show a message


class ComplaintSerializer(serializers.HyperlinkedModelSerializer):
    symptoms = serializers.StringRelatedField(
        read_only=True,
        many=True
    )
    class Meta:
        model = Complaint
        fields = ['url','id', 'symptoms', 'sex', 'year_of_birth', 'age_group', 'patient', 'treated_by']
        extra_kwargs = {
            'patient': {
                'lookup_field': 'username',
                'read_only': True
            },
            'id': {
                'read_only': True
            },
            'treated_by': {
                'lookup_field': 'username',
                'read_only': True
            }
        }

    
    def validate_year_of_birth(self, value):
        if len(str(abs(value))) != 4:
            raise serializers.ValidationError({'error': 'year cannot be more than four digits'})
        elif value > datetime.datetime.now().year:
            raise serializers.ValidationError({'error': 'year is invalid'})
        return value


    def create(self, validated_data):
        return Complaint.objects.create(**validated_data)
    

class SymptomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Symptom
        fields = ['ID', 'Name']
        extra_kwargs = {
            'ID': {'read_only': True},
            'Name': {'read_only': True}
        }


class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    patient = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field = 'username', 
        read_only=True,
    )

    class Meta:
        model = Appointment
        fields = ['url', 'id', 'owner', 'patient', 'date_of_appointment', 'time_of_appointment']
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }

    
    def create(self, validated_data):
        return Appointment.objects.create(**validated_data)
    

    def update(self, instance, validated_data):
        instance.owner = validated_data.get('owner', instance.owner)
        instance.patient = validated_data.get('patient', instance.patient)
        instance.date_of_appointment = validated_data.get('date_of_appointment', instance.date_of_appointment)
        instance.time_of_appointment = validated_data.get('time_of_appointment', instance.time_of_appointment)
        instance.save()
        return instance