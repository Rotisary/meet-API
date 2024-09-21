from rest_framework import serializers
from users.models import User, Profile, DoctorReview, APIUser
from itertools import chain 


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['url', 'email', 'username', 'password', 'password2', 'category', 'first_name', 'last_name', 'phone_number',  'illness', 'meets', 'appointments_in']
        extra_kwargs = {
            'password': {'write_only': True},
            'url': {'lookup_field': 'username'},
            'meets': {'lookup_url_kwarg': 'username'}
        }


    def validate_phone_number(self, value):
        if len(value) == 11:
            letters = chain(range(ord('A'), ord('Z') + 1), range(ord('a'), ord('z') + 1))
            for char in letters:
                if chr(char) in value:
                    raise serializers.ValidationError({'error': 'the phone number is invalid'})           
        elif len(value) > 11 or len(value) < 11:
            raise serializers.ValidationError({'error': "phone number can't be longer or shorter than eleven"})
        return value


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


class APIUserSerializer(serializers.HyperlinkedModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = APIUser
        fields = ['url', 'email', 'username', 'password', 'password2', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {
            'password' : {'write_only': True},
            'url': {'lookup_field': 'username'}
        }

    def save(self):
        user = APIUser(
                email = self.validated_data['email'].lower(),
                username = self.validated_data['username'],
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


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'phone_number']
    

    def validate_phone_number(self, value):
        if len(value) == 11:
            letters = chain(range(ord('A'), ord('Z') + 1), range(ord('a'), ord('z') + 1))
            for char in letters:
                if chr(char) in value:
                    raise serializers.ValidationError({'error': 'the phone number is invalid'})           
        elif len(value) > 11 or len(value) < 11:
            raise serializers.ValidationError({'error': "phone number can't longer or shorter than eleven"})
        return value


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
        fields = ['url', 'user', 'specialized_field', 'patient_type', 'meet', 'appointments_booked', 'reviews']
        extra_kwargs = {
            'url': {'lookup_url_kwarg': 'username'}
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)


class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    writer = serializers.StringRelatedField(read_only=True)
    doctor = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = DoctorReview
        fields = ['writer', 'doctor', 'body', 'stars']
