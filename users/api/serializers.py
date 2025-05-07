from rest_framework import serializers
from users.models import User, Profile, DoctorReview, APIUser
from itertools import chain 


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    complaints = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='complaint-detail',
        many=True
    )
    appointments_in = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='appointment-detail',
        many=True
    )
    class Meta:
        model = User
        fields = ['url', 'id', 'email', 'username', 'password', 'password2', 'category', 'first_name', 'last_name', 'phone_number',  'complaints', 'appointments_in']
        extra_kwargs = {
            'password': {'write_only': True},
            'url': {'lookup_field': 'username'},
            'id': {'read_only': True},
            'phone_number': {'required': False}
        }

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({'password': "second password does not match the first!"})
        return data


    def validate_phone_number(self, value):
        if len(value) == 11:
            letters = chain(range(ord('A'), ord('Z') + 1), range(ord('a'), ord('z') + 1))
            for char in letters:
                if chr(char) in value:
                    raise serializers.ValidationError({'error': 'the phone number is invalid'})           
        elif len(value) > 11 or len(value) < 11:
            raise serializers.ValidationError({'error': "phone number can't be longer or shorter than eleven"})
        return value


    def create(self, validated_data):
        password_two = validated_data.pop('password2', None)
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class APIUserSerializer(serializers.HyperlinkedModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = APIUser
        fields = ['url', 'id', 'email', 'username', 'password', 'password2', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {
            'password' : {'write_only': True},
            'url': {'lookup_field': 'username'},
            'id': {'read_only': True},
            'phone_number': {'required': False}
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
    

    def create(self, validated_data):
        password_two = validated_data.pop('password2', None)
        password = validated_data.pop('password')
        user = APIUser.objects.create(**validated_data)
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
    class Meta:
        model = Profile
        fields = ['url', 'id', 'user', 'slug', 'specialization', 'patient_type', 'appointments_booked', 'reviews', 'rating']
        extra_kwargs = {
            'url': {'lookup_field': 'slug'},
            'id': {'read_only': True},
            'user': {
                'lookup_field': 'username',
                'read_only': True
                },
            'rating': {'read_only': True},
            'slug': {'read_only': True}
        }


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)


class ReviewSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField('get_writer_name')
    doctor = serializers.SerializerMethodField('get_doctor_name')
    class Meta:
        model = DoctorReview
        fields = ['url', 'writer','id', 'doctor', 'body', 'stars']
        extra_kwargs = {
            'id': {'read_only': True}
        }

    
    def get_writer_name(self, review):
        first_name = review.writer.first_name
        last_name = review.writer.last_name
        full_name = f"{first_name} {last_name}"
        return full_name
    

    def get_doctor_name(self, review):
        first_name = review.doctor.user.first_name
        last_name = review.doctor.user.last_name
        full_name = f"{first_name} {last_name}"
        return full_name
