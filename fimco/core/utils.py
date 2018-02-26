from django.contrib.auth.models import User
from django.shortcuts import render

from fimcosite.models import CorporateProfile, CorporateUser, Account
from pochi.models import GroupMember, Group, PaidUser


def render_with_global_data(request, page, context):
    profile = request.user.profile
    if profile.profile_type == 'I':
        group_members_obj = []
        paid_user = None
        try:
            acc = Account.objects.get(profile_id=profile.profile_id).account
        except Account.DoesNotExist:
            acc = None
        try:
            group_account_obj = GroupMember.objects.filter(profile_id=profile.profile_id).only('group_account')
            for group in group_account_obj:
                try:
                    grp_name = Group.objects.get(account=group.group_account).name
                    is_admin = group.admin
                    group_members_obj.append({'name': grp_name, 'admin': is_admin})
                except Group.DoesNotExist:
                    pass

        except GroupMember.DoesNotExist:
            pass

        if acc:
            try:
                paid_user = PaidUser.objects.get(account=acc)
            except PaidUser.DoesNotExist:
                pass

        _context = {
            'profile': profile,
            'groups': group_members_obj,
            'paid': paid_user,
        }
    else:
        pochi = CorporateUser.objects.get(profile_id=profile.profile_id).account
        members = CorporateUser.objects.filter(account=pochi).values_list('profile_id', flat=True)
        company = CorporateProfile.objects.get(account=pochi).company_name
        corporate_users = []
        for member in members:
            corporate_user = User.objects.select_related('profile').get(profile__profile_id=member).get_full_name()
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
