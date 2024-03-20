from rest_framework import serializers
from booking.models import IllnessDetail

class IllnessDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField('get_user_first_name')
    last_name =  serializers.SerializerMethodField('get_user_last_name')

    class Meta:
        model = IllnessDetail
        fields = ['body_part', 'illness', 'age', 'first_name', 'last_name']

    
    def get_user_first_name(self, IllnessDetail):
        first_name = IllnessDetail.patient.first_name
        return first_name
    

    def get_user_last_name(self, IllnessDetail):
        last_name = IllnessDetail.patient.last_name
        return last_name