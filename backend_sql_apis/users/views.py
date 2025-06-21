from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView


from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404


from .models import CustomUser
from .serializers import CustomUserSerializer,LoginSerializer, PasswordResetConfirmSerializer, PasswordResetRequestSerializer, ProfileSerializer
from rest_framework.generics import GenericAPIView
from users.tasks import send_verification_email
from users.throttles import LoginThrottle, PasswordResetThrottle


class CustomUserCreateView(generics.CreateAPIView):
    """Register the user"""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Check if username or email already exists
            if CustomUser.objects.filter(email=serializer.validated_data['email']).exists():
                return Response({'error': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)
            if CustomUser.objects.filter(username=serializer.validated_data['username']).exists():
                return Response({'error': 'Username already taken.'}, status=status.HTTP_400_BAD_REQUEST)

            # Save user as inactive
            user = serializer.save()
            user.is_active = False
            user.save()

            # Generate verification token
            token = default_token_generator.make_token(user)

            # Send verification email
            verification_link = f"http://127.0.0.1:8000/account/verify-email/?uid={user.id}&token={token}"
            send_verification_email.delay(
                subject="Verify your email address",
                message=f"Hi {user.username},\nPlease click the link below to verify your email:\n{verification_link}",
                from_email="dipa.kamble.cerelabs@gmail.com",
                recipient_list=[user.email],
            )

            # Create user and return JWT token
            # user = serializer.save()
            # headers = self.get_success_headers(serializer.data)
            # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

            return Response({"message": "Registered successfully. Please check your email to verify your account."},
                        status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"error": str(ex)},status=status.HTTP_400_BAD_REQUEST)
        
class VerifyEmailView(APIView):
    """Verify user's email address"""

    def get(self, request, *args, **kwargs):
        try:
            uid = request.GET.get('uid')
            token = request.GET.get('token')

            if not uid or not token:
                return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)

            user = get_object_or_404(CustomUser, id=uid)

            if user.is_active:
                return Response({'message': 'Account already verified.'}, status=status.HTTP_200_OK)

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({'message': 'Email verified successfully. You can now log in.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    
class LoginView(GenericAPIView):
    """Login the user"""
    serializer_class = LoginSerializer
    throttle_classes = [LoginThrottle]  # For rate limiting

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data['user']
            access_token = serializer.validated_data['access_token']
            refresh_token = serializer.validated_data['refresh_token']
            

            return Response({
                'email': user.email,
                'username': user.username,
                'access_token': access_token,
                'refresh_token':refresh_token,
                'last_login': user.last_login
            }, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({"error": str(ex)},status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_class=[IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"error":"Refresh token is required"},status=status.HTTP_400_BAD_REQUEST)
            
            access_token= RefreshToken(refresh_token)
            access_token.blacklist()  # Blacklist the refresh token

            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    throttle_classes = [PasswordResetThrottle]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            email = serializer.validated_data['email']
            user = get_object_or_404(CustomUser, email=email)
            
            token = default_token_generator.make_token(user)
            uid = user.pk  # You might later encode this (e.g., using uidb64)
            
            reset_link = f"http://127.0.0.1:8000/account/password-reset-confirm/?uid={uid}&token={token}"

            send_verification_email.delay(
                subject="Password Reset Request",
                message=f"Hi {user.username},\nPlease click the link below to reset your password:\n{reset_link}",
                from_email='dipa.kamble.cerelabs@gmail.com',
                recipient_list=[user.email],
            )

            return Response({'message': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()

            return Response({'message': 'Password reset successful.now you can login again'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProfileUpdateView(generics.GenericAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile = self.serializer_class.get_profile_by_user(request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        profile = self.serializer_class.get_profile_by_user(request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
