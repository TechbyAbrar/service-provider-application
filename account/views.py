from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import (SignupSerialzier, VerifyOTPSerializer, ResendVerifyOTPSerializer, LoginSerializer, 
                          ForgetPasswordSerializer, ResetPasswordSerializer,
                          VerifyForgetPasswordOTPSerializer, UpdateProfileSerializer)

from core.utils import ResponseHandler
from rest_framework.permissions import IsAuthenticated
from account.utils import generate_tokens_for_user
from account.serializers import UserSerializer
from django.conf import settings

# Create your views here.
class RegisterAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerialzier(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return ResponseHandler.created(
            message="Registration successful. OTP sent via SMS.",
            data={
                "user_id": user.user_id,
                "email": user.email,
                "phone": user.phone,
                "is_verified": user.is_verified
            }
        )



class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ResponseHandler.success(
            message="Email verified successfully."
        )


class ResendVerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResendVerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ResponseHandler.success(
            message="A new OTP has been sent to your email."
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = generate_tokens_for_user(user)

        user_data = UserSerializer(user).data

        return ResponseHandler.success(
            message="Login successful",
            data={
                "user": user_data,
                "tokens": tokens
            }
        )

        
from django.db import transaction

class ForgetPasswordView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        """Send OTP to admin email."""
        serializer = ForgetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseHandler.success(
                message="OTP sent to user email successfully."
            )
        return ResponseHandler.bad_request(
            message="Failed to send OTP.",
            errors=serializer.errors
        )


class VerifyForgetPasswordOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Verify OTP and return access token."""
        serializer = VerifyForgetPasswordOTPSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.to_representation(serializer.validated_data)
            return ResponseHandler.success(
                message="OTP verified successfully.",
                data=response_data
            )
        return ResponseHandler.bad_request(
            message="OTP verification failed.",
            errors=serializer.errors
        )


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Reset password after verifying OTP (requires token)."""
        serializer = ResetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return ResponseHandler.success(
                message="Password reset successfully."
            )
        return ResponseHandler.bad_request(
            message="Password reset failed.",
            errors=serializer.errors
        )

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

# Update Profile
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return ResponseHandler.success(
            message="User profile fetched successfully.",
            data={"user": serializer.data}
        )

    def patch(self, request):
        try:
            serializer = UpdateProfileSerializer(
                instance=request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            return ResponseHandler.success(
                message="Profile updated successfully.",
                data={"user": UserSerializer(user).data}
            )

        except Exception as exc:
            # Local safe fallback — avoids 'request' bug in ResponseHandler debug
            import traceback
            debug_info = traceback.format_exc().splitlines()[-5:]

            return ResponseHandler.error(
                message="Profile update failed due to an unexpected error.",
                errors=str(exc),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                extra={"debug": debug_info}
            )
            
            
        
# dashboard
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from .serializers import DashboardSerializer, UserSerializer
from .services import DashboardService
from .pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)

class DashboardAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            queryset = (
                DashboardService.get_users_queryset()
                .prefetch_related("subscriptions__plan")
            )

            paginator = StandardResultsSetPagination()
            paginated_users = paginator.paginate_queryset(queryset, request)

            users_serializer = UserSerializer(paginated_users, many=True)

            data = {
                "total_users": DashboardService.get_total_users(),
                "total_verified": DashboardService.get_total_verified(),
                "total_unverified": DashboardService.get_total_unverified(),
                "total_earnings": DashboardService.get_total_earnings(),
                "users": users_serializer.data,
            }

            serializer = DashboardSerializer(instance=data)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            logger.exception("Error fetching dashboard data")
            return Response(
                {"detail": "Error fetching dashboard data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# User Detail API
class UserDetailAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, user_id):
        try:
            from account.models import User
            user = User.objects.prefetch_related("subscriptions__plan").filter(user_id=user_id).first()
            if not user:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error fetching user {user_id}")
            return Response({"detail": "Error fetching user data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
# social auth

from .utils import validate_google, validate_microsoft, validate_apple
from .services import social_login
from .serializers import UserSerializer

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("id_token")
        if not token:
            return ResponseHandler.bad_request(message="id_token required")

        data = validate_google(token)
        if not data:
            return ResponseHandler.bad_request(message="Invalid Google token")

        try:
            user = social_login("google", data)
            return ResponseHandler.success(
                message="Google login successful.",
                data=UserSerializer(user).data
            )
        except Exception as e:
            return ResponseHandler.generic_error(exception=e)


class MicrosoftLoginView(APIView):
    def post(self, request):
        token = request.data.get("access_token")
        if not token:
            return ResponseHandler.bad_request(message="access_token required")

        data = validate_microsoft(token)
        if not data:
            return ResponseHandler.bad_request(message="Invalid Microsoft token")

        try:
            user = social_login("microsoft", data)
            return ResponseHandler.success(
                message="Microsoft login successful.",
                data=UserSerializer(user).data
            )
        except Exception as e:
            return ResponseHandler.generic_error(exception=e)


class AppleLoginView(APIView):
    def post(self, request):
        token = request.data.get("identity_token")
        if not token:
            return ResponseHandler.bad_request(message="identity_token required")

        data = validate_apple(token)
        if not data:
            return ResponseHandler.bad_request(message="Invalid Apple token")

        try:
            user = social_login("apple", data)
            return ResponseHandler.success(
                message="Apple login successful.",
                data=UserSerializer(user).data
            )
        except Exception as e:
            return ResponseHandler.generic_error(exception=e)
