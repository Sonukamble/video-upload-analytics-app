from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import ValidationError
from users.models import CustomUser

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Handle duplicate emails or empty email issues during social login.
        """
        email = sociallogin.account.extra_data.get('email')
        if not email:
            # Raise an error or handle cases where email is not provided
            raise ValidationError("This Google account does not have an associated email.")

        try:
            # Check if the email already exists
            user = CustomUser.objects.get(email=email)
            sociallogin.user = user  # Link the social account to the existing user
        except CustomUser.DoesNotExist:
            pass  # No user exists with this email, proceed as normal
