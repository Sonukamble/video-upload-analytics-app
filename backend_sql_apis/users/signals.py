from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from allauth.socialaccount.models import SocialAccount
from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender,instance, created, **kwargs):
    """ Create a new profile with default values"""
    if created:
        Profile.objects.create(
            user=instance,
            title=instance.username,  
            image='default_profile_image_url',  
            description=''
        )

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_profile_with_google_data(sender, instance, **kwargs):
    """ update the profile"""
    try:
        social_account= SocialAccount.objects.get(user=instance,provider='google')
        google_data=social_account.extra_data
        image_url=google_data.get('picture')
        title = instance.username
        description = ''

        # Update the profile with Google data
        profile, created = Profile.objects.get_or_create(user=instance)
        profile.image = image_url
        profile.title = title
        profile.description = description
        profile.save()
    except SocialAccount.DoesNotExist:
        # If the user didn't log in via Google, ensure basic data is still set
        profile, created = Profile.objects.get_or_create(user=instance)
        if not profile.image:  # Set a default image if not already set
            profile.image = 'default_profile_image_url'  # Replace with your default image URL
        if not profile.title:
            profile.title = instance.username  # Use the username as the title
        profile.save()