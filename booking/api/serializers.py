from rest_framework import serializers
from booking.models import Illness, Appointment


class IllnessSerializer(serializers.HyperlinkedModelSerializer):
    patient = serializers.HyperlinkedRelatedField(
        view_name='user-detail', 
        lookup_field='username',  
        read_only=True
    )
    treated_by = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field='username',
        read_only=True
    )
    class Meta:
        model = Illness
        fields = ['url', 'body_part', 'specific_illness', 'age', 'patient', 'treated_by']


class AppointmentSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    patient = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field = 'username', 
        read_only=True,
    )

    class Meta:
        model = Appointment
        fields = ['url', 'owner', 'patient', 'date_of_appointment', 'time_of_appointment']

    
    def create(self, validated_data):
        return Appointment.objects.create(**validated_data)
    

    def update(self, instance, validated_data):
        instance.owner = validated_data.get('owner', instance.owner)
        instance.patient = validated_data.get('patient', instance.patient)
        instance.date_of_appointment = validated_data.get('date_of_appointment', instance.date_of_appointment)
        instance.time_of_appointment = validated_data.get('time_of_appointment', instance.time_of_appointment)
        instance.save()
        return instance
 