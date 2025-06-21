from . import views
from django.urls import path,include
 
from .views import CustomUserCreateView,LoginView,LogoutView, ProfileUpdateView, VerifyEmailView, PasswordResetRequestView, PasswordResetConfirmView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', CustomUserCreateView.as_view(), name='create-user'),
    path('login/', LoginView.as_view(), name='login-user'),

    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),

    # password reset 
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Add the refresh token endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout-user'),

    # update the profile
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),

]
