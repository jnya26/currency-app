from concurrent.futures import ThreadPoolExecutor  # noqa
from datetime import datetime, timedelta
import concurrent
import requests
import pandas as pd
import time

from dateutil.utils import today
from django.core.mail import EmailMessage

from config import settings
from config.celery import app

from config.settings import BASE_DIR
from currency.models import ExchangeRateProvider, ExchangeRate

@app.task
def send_custom_mail():
    today = datetime.today()
    day_ago = today - timedelta(days=1)

    provider_privat = ExchangeRateProvider.objects.filter(name='PrivatBank',
                                                          api_url="https://api.privatbank.ua/p24api/exchange_rates") \
        .first()
    provider_mono = ExchangeRateProvider.objects.filter(name='MonoBank',
                                                        api_url="https://api.monobank.ua/bank/currency").first()
    privat_currency = ExchangeRate.objects.filter(for_date=day_ago, provider=provider_privat).values('provider__name',
                                                                                                     'base_currency',
                                                                                                     'currency',
                                                                                                     'sale_rate',
                                                                                                     'buy_rate',
                                                                                                     'for_date')

    mono_currencies = ExchangeRate.objects.filter(for_date=day_ago, provider=provider_mono).values('provider__name',
                                                                                                   'base_currency',
                                                                                                   'currency',
                                                                                                   'sale_rate',
                                                                                                   'buy_rate',
                                                                                                   'for_date')
    print(mono_currencies)
    currency = privat_currency.union(mono_currencies)

    dp = pd.DataFrame(currency)
    dp.index = range(1, len(dp) + 1)
    output_file_path = BASE_DIR / 'currencies.csv'
    dp.to_csv(output_file_path)

    email = EmailMessage(
        subject='Currencies',
        body='Please find attached the currencies file.',
        from_email='jenya26@gmail.com',
        to='fifand1005@gmail.com',
    )

    email.attach_file(output_file_path)
    email.send()

