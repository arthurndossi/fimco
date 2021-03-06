from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile, CorporateProfile, KYC, Account, CorporateUser


class CorporateProfileAdmin(admin.ModelAdmin):
    list_filter = ('indemnity',)
    list_display = ('company_name', 'address', 'account', 'indemnity')


class CorporateUserAdmin(admin.ModelAdmin):
    list_filter = ('admin',)
    list_display = ('profile_id', 'account', 'admin')


class KYCAdmin(admin.ModelAdmin):
    list_display = ('account', 'created_on', 'kyc_type', 'id_number', 'document')


class AccountAdmin(admin.ModelAdmin):
    list_display = ('profile_id', 'created_on', 'account', 'current_balance', 'available_balance',
                    'ts_current_bal', 'ts_available_bal', 'status', 'allow_overdraft')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


# Define a new User admin
class FimcoUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__profile_type')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(FimcoUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, FimcoUserAdmin)
admin.site.register(CorporateProfile, CorporateProfileAdmin)
admin.site.register(CorporateUser, CorporateUserAdmin)
admin.site.register(KYC, KYCAdmin)
admin.site.register(Account, AccountAdmin)
