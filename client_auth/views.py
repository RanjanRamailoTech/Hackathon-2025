from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import CompanySignupSerializer, CompanyLoginSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class CompanySignupView(APIView):
    """View for handling company signup requests."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Register a new company user.

        Args:
            request (HttpRequest): The incoming HTTP request containing signup data.

        Returns:
            Response: A response indicating success with the company ID or validation errors.

            - On success: HTTP 201 Created with a message and company ID.
            - On failure: HTTP 400 Bad Request with serializer errors.

        """
        serializer = CompanySignupSerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()
            return Response(
                {"message": "Company registered successfully", "company_id": company.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyLoginView(APIView):
    """View for handling company login requests."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Authenticate a company user and issue JWT tokens.

        Args:
            request (HttpRequest): The incoming HTTP request containing login credentials.

        Returns:
            Response: A response containing JWT tokens or an error message.

            - On success: HTTP 200 OK with refresh and access tokens.
            - On invalid credentials: HTTP 401 Unauthorized with an error message.
            - On validation failure: HTTP 400 Bad Request with serializer errors.

        """
        serializer = CompanyLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)