from django.contrib import messages
from django.contrib.auth.models import User

from .models import CorporateProfile, Profile


class CorporateBackend:

    def __init__(self):
        pass

    @staticmethod
    def authenticate(request, username=None, password=None, pochi=None, access='normal'):

        if access == 'normal':
            try:
                company = CorporateProfile.objects.get(account=pochi)
                if company:
                    try:
                        user = Profile.objects.filter(user__email=username)
                    except Profile.DoesNotExist:
                        user = None
                    if user:
                        if user.check_password(password):
                            user = user
                        else:
                            user = None
                            messages.error(request, 'Incorrect credentials!')
                    else:
                        messages.error(request, 'Incorrect credentials!')
                    return user
            except CorporateProfile.DoesNotExist:
                return None
        else:
            try:
                company = CorporateProfile.objects.get(account=pochi)
                if company:
                    try:
                        user = Profile.objects.filter(user__email=username)
                    except Profile.DoesNotExist:
                        user = None
                    if user:
                        if user.profile_id == company.admin:
                            if user.check_password(password):
                                user = user
                            else:
                                user = None
                                messages.error(request, 'Incorrect credentials!')
                        else:
                            messages.error(request, 'You need admin rights to aad a new user.\r\n'
                                           'Please contact your corporate admin to add another user.')
                    else:
                        messages.error(request, 'Incorrect credentials!')
                    return user
            except CorporateProfile.DoesNotExist:
                return None

    # Required for your backend to work properly - unchanged in most scenarios
    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
