from rest_framework import serializers
from .models import CustomUser,Profile
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.utils.timezone import now
from django.contrib.auth import get_user_model

from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import default_token_generator


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True,validators=[validate_password])  # Write-only for security
    token = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'created_at', 'updated_at','token']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        # Use the custom manager to create the user
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', ''),
            password=validated_data['password']
        )
        return user
    
    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])  # Hash the password
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    token = serializers.SerializerMethodField()
    refresh_token = serializers.SerializerMethodField()

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)

    def get_refresh_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email:
            raise serializers.ValidationError({"email": "This field is required."})
        if not password:
            raise serializers.ValidationError({"password": "This field is required."})

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid email or password"})

        # Update last login
        user.last_login = now()
        user.save()

        return {'user': user, 'access_token': self.get_token(user), 'refresh_token': self.get_refresh_token(user)}

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("No user is associated with this email address.")
        return email

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        try:
            user = CustomUser.objects.get(pk=attrs['uid'])
        except user.DoesNotExist:
            raise serializers.ValidationError("Invalid user ID.")

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired token.")

        attrs['user'] = user
        return attrs
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'title', 'image', 'description']
        read_only_fields = ['id']

    @staticmethod
    def get_profile_by_user(user):
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            raise serializers.ValidationError("Profile does not exist for this user.")


    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


    # def create(self, validated_data):
    #     # If someone wants to create Profile
    #     return Profile.objects.create(**validated_data)