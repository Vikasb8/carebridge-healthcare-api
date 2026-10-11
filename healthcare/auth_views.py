from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, RegisterSerializer


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Registers a new healthcare user with name, email, and password.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Register a new user",
        description="Creates a new user account with name, email, and password. Returns user profile details.",
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(description="User successfully registered"),
            400: OpenApiResponse(description="Validation error (e.g., email already exists, weak password)"),
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        return Response(
            {
                "message": "Registration successful.",
                "user": {
                    "id": user.id,
                    "name": full_name,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/
    Logs in an existing user with email and password, returning JWT access and refresh tokens.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Log in user and obtain JWT tokens",
        description="Authenticates credentials and returns JWT access and refresh tokens along with user info.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Authentication successful, returns JWT tokens"),
            400: OpenApiResponse(description="Invalid email or password"),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        return Response(
            {
                "message": "Login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "name": full_name,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )
