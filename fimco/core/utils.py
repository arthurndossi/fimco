from django.contrib.auth.models import User
from django.shortcuts import render

from pochi.models import GroupMember, Group, PaidUser

from fimcosite.models import CorporateProfile, Profile


def render_with_global_data(request, page, context):
    profile = request.user.profile
    if profile.profile_type == 'I':
        group_members_obj = []
        paid_user = None
        try:
            group_account_obj = GroupMember.objects.filter(profile_id=profile.profile_id).only('group_account')
            for group in group_account_obj:
                try:
                    grp_name = Group.objects.get(group_account=group.group_account).name
                    is_admin = group.admin
                    group_members_obj.append({'name': grp_name, 'admin': is_admin})
                except Group.DoesNotExist:
                    pass

        except GroupMember.DoesNotExist:
            pass

        try:
            paid_user = PaidUser.objects.get(profile_id=profile.profile_id)
        except PaidUser.DoesNotExist:
            pass

        _context = {
            'profile': profile,
            'groups': group_members_obj,
            'paid': paid_user
        }
    else:
        company = CorporateProfile.objects.get(profile_id=profile.profile_id).company_name
        members = Profile.objects.filter(profile_id=profile.profile_id).values_list('user__username', flat=True)
        corporate_users = []
        for member in members:
            user_obj = User.objects.select_related('profile').get(username=member)
            corporate_user = user_obj.get_full_name()
            corporate_users.append(corporate_user)
        _context = {
            'profile': profile,
            'company': company,
            'users': corporate_users,
        }
    if context:
        context.update(_context)
    else:
        context = _context
    return render(request, page, context)
