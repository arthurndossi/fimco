from django.shortcuts import render

from pochi.models import GroupMembers, Group, PremiumUsers


def render_with_global_data(request, page, context):
    profile = request.user.profile
    group_members_obj = []
    paid_user = None
    try:
        group_account_obj = GroupMembers.objects.filter(profile_id=profile.profile_id).only('group_account')
        for group in group_account_obj:
            try:
                grp_name = Group.objects.get(group_account=group.group_account).name
                group_members_obj.append(grp_name)
            except Group.DoesNotExist:
                pass

    except GroupMembers.DoesNotExist:
        pass

    try:
        paid_user = PremiumUsers.objects.get(profile_id=profile.profile_id)
    except PremiumUsers.DoesNotExist:
        pass

    _context = {
        'groups': group_members_obj,
        'paid': paid_user
    }
    if context:
        context.update(_context)
    else:
        context = _context
    return render(request, page, context)
