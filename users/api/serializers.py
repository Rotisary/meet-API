from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from users.models import User
from booking.api.serializers import IllnessDetailSerializer
from booking.models import IllnessDetail


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'category', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {
            'password': {'write_only': True}
        }


    def save(self):
        user = User(
            email = self.validated_data['email'].lower(),
            username = self.validated_data['username'],
            category = self.validated_data['category'],
            first_name = self.validated_data['first_name'].lower(),
            last_name = self.validated_data['last_name'].lower(),
            phone_number = self.validated_data['phone_number']
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        

        if password != password2:
            raise serializers.ValidationError({'password': "second password does not match the first!"})
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)