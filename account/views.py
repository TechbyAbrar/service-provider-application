from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import (SignupSerialzier, VerifyOTPSerializer, ResendVerifyOTPSerializer, LoginSerializer, ForgetPasswordSerializer, ResetPasswordSerializer, VerifyForgetPasswordOTPSerializer, UpdateProfileSerializer)

from core.utils import ResponseHandler
from rest_framework.permissions import IsAuthenticated
from account.utils import generate_tokens_for_user
from account.serializers import UserSerializer


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