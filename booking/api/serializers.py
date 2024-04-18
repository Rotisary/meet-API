from rest_framework import serializers
from booking.models import Illness


class IllnessSerializer(serializers.HyperlinkedModelSerializer):
    patient = serializers.HyperlinkedRelatedField(
        view_name='user-detail', 
        lookup_field='username',  
        read_only=True
    )

    class Meta:
        model = Illness
        fields = ['url', 'body_part', 'specific_illness', 'age', 'patient', 'treated_by']
 