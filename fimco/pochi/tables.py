import django_tables2 as tables

from .models import Transaction


class TransactionTable(tables.Table):
    class Meta:
        model = Transaction
        fields = ('account', 'service', 'channel', 'dest_account', 'currency', 'amount', 'charge', 'status')
        attrs = {'class': 'table table-condensed'}
