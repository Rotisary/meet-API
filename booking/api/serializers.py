from rest_framework import serializers
from booking.models import IllnessDetail

class IllnessDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='patient.first_name', read_only=True)
    last_name =  serializers.CharField(source='patient.last_name', read_only=True)

    class Meta:
        model = IllnessDetail
        fields = ['body_part', 'illness', 'age', 'first_name', 'last_name']