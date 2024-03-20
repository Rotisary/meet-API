from rest_framework import serializers
from booking.models import IllnessDetail

class IllnessDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = IllnessDetail
        fields = ['body_part', 'illness', 'age']