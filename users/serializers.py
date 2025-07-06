from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Handle user registration with password confirmation"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta: 
        model = User
        fields = ('email', 'username','password', 'password2', 'bio', 'location')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords don't match!")
        return attrs

    def create(self, validated_data):
        # Remove password2 since it's not a model field
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Complete user profile with computed fields"""
    recipes_count = serializers.ReadOnlyField()
 
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'bio', 'profile_picture', 'location', 
                 'date_joined','recipes_count', 'is_chef_verified')
        read_only_fields = ('id', 'email', 'date_joined')

class UserUpdateSerializer(serializers.ModelSerializer):
    """For updating user profiles"""
    class Meta:
        model = User
        fields = ('bio', 'profile_picture', 'location')