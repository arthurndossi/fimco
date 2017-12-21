from django.contrib.auth.models import User

from .models import CorporateProfile, Profile


class CorporateBackend:

    def authenticate(self, username=None, password=None, pochi=None):

        try:
            company = CorporateProfile.objects.get(profile_id=pochi)
            if company:
                try:
                    user = Profile.objects.filter(user__username=username, profile_id=pochi)
                except Profile.DoesNotExist:
                    user = None
                if user:
                    if user.check_password(password):
                        user = user
                    else:
                        user = None
                return user
        except CorporateProfile.DoesNotExist:
            return None

    # Required for your backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
