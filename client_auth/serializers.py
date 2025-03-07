from rest_framework import serializers
from django.contrib.auth.models import User
from Job_opening.models import Company  # Import from Job_opening app

class CompanySignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    
    class Meta:
        model = Company
        fields = ["name", "email", "username", "password"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        # Create User instance
        user_data = {
            "username": validated_data.pop("username"),
            "email": validated_data["email"],
            "password": validated_data.pop("password"),
        }
        user = User.objects.create_user(**user_data)
        
        # Create Company instance linked to User
        company = Company.objects.create(user=user, **validated_data)
        return company

class CompanyLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})