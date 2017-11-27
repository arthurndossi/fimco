from django.contrib import admin

from .models import Group, GroupMember, Transaction, Ledger, BalanceSnapshot, ExternalAccount, \
    Notification, PaidUser, Charge, CashOut


class GroupAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'name', 'group_account')


class GroupMembersAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'group_account', 'profile_id', 'admin')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('fulltimestamp', 'profile_id', 'account', 'msisdn', 'external_walletid', 'service', 'channel',
                    'dest_account', 'amount', 'charge', 'currency', 'reference', 'status', 'resultcode', 'message',
                    'processed_timestamp')


class LedgerAdmin(admin.ModelAdmin):
    list_display = ('fulltimestamp', 'profile_id', 'account', 'trans_type', 'service', 'channel', 'amount', 'currency',
                    'reference', 'obal', 'cbal')


class BalanceSnapshotAdmin(admin.ModelAdmin):
    list_display = ('fulltimestamp', 'profile_id', 'account', 'closing_balance', 'bonus_closing_balance')


class ExternalAccountAdmin(admin.ModelAdmin):
    list_display = ('profile_id', 'account_name', 'account_number', 'nickname', 'institution_name',
                    'institution_branchcode', 'institution_code', 'account_type')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('profile_id', 'fulltimestamp', 'message', 'read_status')


class PaidUserAdmin(admin.ModelAdmin):
    list_display = ('profile_id', 'level', 'start_date', 'end_date')


class ChargeAdmin(admin.ModelAdmin):
    list_display = ('service', 'charge')


class CashOutAdmin(admin.ModelAdmin):
    list_display = ('ext_entity', 'ext_acc_no', 'amount', 'status')


admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMember, GroupMembersAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Ledger, LedgerAdmin)
admin.site.register(BalanceSnapshot, BalanceSnapshotAdmin)
admin.site.register(ExternalAccount, ExternalAccountAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(PaidUser, PaidUserAdmin)
admin.site.register(Charge, ChargeAdmin)
admin.site.register(CashOut, CashOutAdmin)
