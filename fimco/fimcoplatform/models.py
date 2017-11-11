from django.db import models


class ExchangeRates(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    base_currency = models.CharField(max_length=4)
    counter_currency = models.CharField(max_length=4)
    change = models.DecimalField(max_digits=6, decimal_places=4)
    current_rate = models.DecimalField(max_digits=6, decimal_places=4)
    record_datetime = models.DateTimeField()
    prev_rate = models.DecimalField(max_digits=6, decimal_places=4)
    prev_rate_timestamp = models.DateTimeField()


class OvernightInterest(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    current_rate = models.DecimalField(max_digits=6, decimal_places=4)
    record_datetime = models.DateTimeField()
    weighted_avg_rate = models.DecimalField(max_digits=6, decimal_places=4)
    prev_rate = models.DecimalField(max_digits=6, decimal_places=4)
    prev_rate_timestamp = models.DateTimeField()


class Tbill(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    record_datetime = models.DateTimeField()
    due_date = models.DateField()
    no_of_bids = models.IntegerField()
    no_of_successful_bids = models.IntegerField()
    highest_bid_percent = models.DecimalField(max_digits=4, decimal_places=2)
    lowest_bid_percent = models.DecimalField(max_digits=4, decimal_places=2)
    minimum_success_price = models.DecimalField(max_digits=4, decimal_places=2)
    weighted_avg_price_success = models.DecimalField(max_digits=4, decimal_places=2)
    weighted_avg_yield_annum = models.DecimalField(max_digits=4, decimal_places=2)
    amount_offered = models.DecimalField(max_digits=6, decimal_places=2)  # 000,0000
    total_tender = models.DecimalField(max_digits=6, decimal_places=2)  # 000,0000
    under_over_subscribed = models.DecimalField(max_digits=6, decimal_places=2)  # 000,0000
    successful_bids = models.DecimalField(max_digits=6, decimal_places=2)  # 000,0000


class Tbond(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    record_datetime = models.DateTimeField()
    redemption_date = models.DateField()
    no_of_bids = models.IntegerField()
    no_of_successful_bids = models.IntegerField()
    minimum_successful_price = models.DecimalField(max_digits=4, decimal_places=2)
    weighted_avg_price_success = models.DecimalField(max_digits=4, decimal_places=2)
    weighted_avg_to_maturity = models.DecimalField(max_digits=4, decimal_places=2)
    weighted_avg_coupon_yield = models.DecimalField(max_digits=4, decimal_places=2)
    amount_offered = models.DecimalField(max_digits=6, decimal_places=2)  # 000,0000
    total_tender = models.DecimalField(max_digits=6, decimal_places=2)  # 000,0000
    under_over_subscribed = models.DecimalField(max_digits=6, decimal_places=2)  # 000,0000
    successful_bids = models.DecimalField(max_digits=6, decimal_places=2)  # 000,0000


class GDP(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    year = models.IntegerField()
    value = models.DecimalField(max_digits=2, decimal_places=2)


class Inflation(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    year = models.IntegerField()
    month = models.IntegerField()  # set min max+
    value = models.DecimalField(max_digits=2, decimal_places=2)


class CurrentAccountMonthly(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    year = models.IntegerField()
    month = models.IntegerField()  # set min max
    value = models.DecimalField(max_digits=5, decimal_places=2)


class CurrentAccountYearly(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    year = models.IntegerField()
    value = models.DecimalField(max_digits=2, decimal_places=2)


class ImportExportMonthly(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    year = models.IntegerField()
    month = models.IntegerField()  # set min max
    import_value = models.DecimalField(max_digits=6, decimal_places=2)
    export_value = models.DecimalField(max_digits=6, decimal_places=2)


class ImportExportYearly(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    year = models.IntegerField()
    import_value = models.DecimalField(max_digits=6, decimal_places=2)
    export_value = models.DecimalField(max_digits=6, decimal_places=2)


class LiborRates(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=False, auto_now_add=False)
    value_date = models.DateTimeField()
    overnight_rate = models.DecimalField(max_digits=6, decimal_places=2)
    m1_rate = models.DecimalField(max_digits=6, decimal_places=2)
    m3_rate = models.DecimalField(max_digits=6, decimal_places=2)
    m6_rate = models.DecimalField(max_digits=6, decimal_places=2)
    m12_rate = models.DecimalField(max_digits=6, decimal_places=2)
