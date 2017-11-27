from django.contrib import admin

from .models import ExchangeRate, LiborRate, Tbond, Tbill, OvernightInterest, CurrentMonthlyAccount, \
    CurrentYearlyAccount, MonthlyImportExport, GDP, YearlyImportExport, Inflation


class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('created_on',
                    'modified_on',
                    'base_currency',
                    'counter_currency',
                    'change',
                    'current_rate',
                    'record_datetime',
                    'prev_rate',
                    'prev_rate_timestamp'
                    )


class OvernightInterestAdmin(admin.ModelAdmin):
    list_display = ('created_on',
                    'modified_on',
                    'current_rate',
                    'record_datetime',
                    'weighted_avg_rate',
                    'prev_rate',
                    'prev_rate_timestamp'
                    )


class TbillAdmin(admin.ModelAdmin):
    list_display = ('created_on',
                    'modified_on',
                    'record_datetime',
                    'due_date',
                    'type',
                    'no_of_bids',
                    'no_of_successful_bids',
                    'highest_bid_percent',
                    'lowest_bid_percent',
                    'minimum_success_price',
                    'weighted_avg_price_success',
                    'weighted_avg_yield_annum',
                    'amount_offered',
                    'total_tender',
                    'under_over_subscribed',
                    'successful_bids'
                    )


class TbondAdmin(admin.ModelAdmin):
    list_display = ('created_on',
                    'modified_on',
                    'record_datetime',
                    'redemption_date',
                    'type',
                    'no_of_bids',
                    'no_of_successful_bids',
                    'minimum_successful_price',
                    'weighted_avg_price_success',
                    'weighted_avg_to_maturity',
                    'weighted_avg_coupon_yield',
                    'amount_offered',
                    'total_tender',
                    'under_over_subscribed',
                    'successful_bids'
                    )


class InflationAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'modified_on', 'year', 'month', 'value')


class LiborRateAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'modified_on', 'value_date', 'overnight_rate', 'm1_rate', 'm3_rate', 'm6_rate', 'm12_rate')


class MonthlyImportExportAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'modified_on', 'year', 'month', 'import_value', 'export_value')


class YearlyImportExportAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'modified_on', 'year', 'import_value', 'export_value')


class CurrentMonthlyAccountAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'modified_on', 'year', 'month', 'value')


class CurrentYearlyAccountAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'modified_on', 'year', 'value')


class GDPAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'modified_on', 'year', 'value')

admin.site.register(ExchangeRate, ExchangeRateAdmin)
admin.site.register(OvernightInterest, OvernightInterestAdmin)
admin.site.register(Tbill, TbillAdmin)
admin.site.register(Tbond, TbondAdmin)
admin.site.register(Inflation, InflationAdmin)
admin.site.register(LiborRate, LiborRateAdmin)
admin.site.register(MonthlyImportExport, MonthlyImportExportAdmin)
admin.site.register(YearlyImportExport, YearlyImportExportAdmin)
admin.site.register(CurrentMonthlyAccount, CurrentMonthlyAccountAdmin)
admin.site.register(CurrentYearlyAccount, CurrentYearlyAccountAdmin)
admin.site.register(GDP, GDPAdmin)
