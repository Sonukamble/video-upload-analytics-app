# accounts/throttles.py

from rest_framework.throttling import SimpleRateThrottle

class LoginThrottle(SimpleRateThrottle):
    scope = 'login'  # this should match settings.py throttle rate key

    def get_cache_key(self, request, view):
        email = request.data.get('email')
        if not email:
            return self.get_ident(request)
        return f'throttle_login_{email}'


class PasswordResetThrottle(SimpleRateThrottle):
    scope = 'password_reset'

    def get_cache_key(self, request, view):
        email = request.data.get('email')
        if not email:
            return self.get_ident(request)
        return f'throttle_login_{email}'