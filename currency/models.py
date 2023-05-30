from datetime import datetime

from django.db import models


class Rate(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Create your models here.
class ExchangeRateProvider(models.Model):
    name = models.CharField(max_length=20)
    api_url = models.URLField()
    logo_url = models.URLField(default="#")


class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length=20)
    currency = models.CharField(max_length=20)

    sale_rate = models.DecimalField(max_digits=10, decimal_places=4)
    buy_rate = models.DecimalField(max_digits=10, decimal_places=4)

    provider = models.ForeignKey(ExchangeRateProvider, on_delete=models.CASCADE)
    added_date = models.DateField(default=datetime.utcnow)
    for_date = models.DateField(default=datetime.utcnow)
