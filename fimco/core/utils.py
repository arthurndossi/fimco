from django.shortcuts import render

from pochi.models import GroupMembers, Group


def render_with_global_data(request, page, context):
    profile = request.user.profile
    group_members_obj = []
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
    _context = {
        'groups': group_members_obj,
    }
    if context:
        context.update(_context)
    else:
        context = _context
    return render(request, page, context)
