from rest_framework import serializers
from users.models import User, Profile


class RegistrationSerializer(serializers.HyperlinkedModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['url', 'email', 'username', 'password', 'password2', 'category', 'first_name', 'last_name', 'phone_number']
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


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'email', 'username', 'category', 'first_name', 'last_name', 'phone_number', 'illness']
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field='username',
        read_only=True
    )
    meet = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        lookup_field='username',
        read_only=True,
        many=True
    )
    class Meta:
        model = Profile
        fields = ['url', 'user', 'specialized_field', 'doctor_type', 'meet']
        extra_kwargs = {
            'url': {'lookup_url_kwarg': 'username'}
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
