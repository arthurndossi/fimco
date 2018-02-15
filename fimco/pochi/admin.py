from django.contrib import admin

from .models import Group, GroupMember, Transaction, Ledger, BalanceSnapshot, ExternalAccount, \
    PaidUser, Charge, CashOut, Rate


class GroupAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'name', 'account')


class GroupMembersAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'group_account', 'profile_id', 'admin')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('full_timestamp', 'profile_id', 'account', 'msisdn', 'trans_id', 'service', 'channel', 'mode',
                    'dst_account', 'amount', 'charge', 'reference', 'status', 'result_code',
                    'message', 'processed_timestamp')


class LedgerAdmin(admin.ModelAdmin):
    list_display = ('full_timestamp', 'profile_id', 'account', 'trans_type', 'trans_id', 'amount', 'mode', 'reference',
                    'available_o_bal', 'available_c_bal', 'current_o_bal', 'current_c_bal')


class BalanceSnapshotAdmin(admin.ModelAdmin):
    list_display = ('full_timestamp', 'profile_id', 'account', 'available_closing_balance', 'current_closing_balance',
                    'bonus_closing_balance')


class ExternalAccountAdmin(admin.ModelAdmin):
    list_display = ('profile_id', 'account_name', 'account_number', 'institution_name', 'institution_branch',
                    'institution_code', 'account_type')


class PaidUserAdmin(admin.ModelAdmin):
    list_display = ('profile_id', 'level', 'start_date', 'end_date')


class ChargeAdmin(admin.ModelAdmin):
    list_display = ('service', 'charge')


class CashOutAdmin(admin.ModelAdmin):
    list_display = ('ext_entity', 'ext_acc_no', 'amount', 'status')


class RateAdmin(admin.ModelAdmin):
    list_display = ('full_timestamp', 'rate')


admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMember, GroupMembersAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Ledger, LedgerAdmin)
admin.site.register(BalanceSnapshot, BalanceSnapshotAdmin)
admin.site.register(ExternalAccount, ExternalAccountAdmin)
admin.site.register(PaidUser, PaidUserAdmin)
admin.site.register(Charge, ChargeAdmin)
admin.site.register(CashOut, CashOutAdmin)
admin.site.register(Rate, RateAdmin)
