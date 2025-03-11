from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
import pyotp
import random
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

User = get_user_model()

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            otp = str(random.randint(100000, 999999))  # Generate OTP
            user.otp_secret = otp
            user.save()

            # Send OTP to email
            send_mail(
                "Password Reset OTP",
                f"Your OTP is {otp}",
                "priyalotiya25@gmail.com",  # Change to your email
                [email],
                fail_silently=False,
            )

            return Response({'message': 'OTP sent to email'}, status=status.HTTP_200_OK)
        return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        user = User.objects.filter(email=email, otp_secret=otp).first()
        if user:
            user.set_password(new_password)  # Update password
            user.otp_secret = None  # Clear OTP after use
            user.save()
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
