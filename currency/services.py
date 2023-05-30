from concurrent.futures import ThreadPoolExecutor # noqa
from datetime import datetime, timedelta, date
from currency.models import ExchangeRate, ExchangeRateProvider
from config import settings

import requests
import concurrent
import pycountry


class ExchangeRatesServices:
    CURRENCIES = ['USD', 'EUR']

    def get_rates(self):
        url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
        logo_url = "https://avatars.githubusercontent.com/u/95229470?s=280&v=4"

        response = requests.get(url)
        data = response.json()

        currency_rate = []
        if ExchangeRateProvider.objects.filter(name='PrivatBank', logo_url=logo_url, api_url=url):

            provider = \
                ExchangeRateProvider.objects.get(name='PrivatBank', logo_url=logo_url, api_url=url)
            print(provider)
        else:
            provider = \
                ExchangeRateProvider.objects.get_or_create(name='PrivatBank', logo_url=logo_url, api_url=url)[0]
            print(provider)

        for d in data:
            if d['ccy'] not in self.CURRENCIES:
                continue
            else:
                if ExchangeRate.objects.filter(base_currency=d['base_ccy'], currency=d['ccy'],
                                               provider=provider, added_date=datetime.today(), sale_rate=d['sale'],
                                               buy_rate=d['buy']).exists():
                    continue
                else:
                    currency = ExchangeRate(
                        base_currency=d['base_ccy'],
                        currency=d['ccy'],
                        sale_rate=d['sale'],
                        buy_rate=d['buy'],
                        provider=provider)

                    currency.save()
                    currency_rate.append(currency)

        return currency_rate


class ExchangeRatesServicesMono:
    CURRENCIES = ['USD', 'EUR', 'UAH']

    def get_rates_mono(self):
        try:
            url = "https://api.monobank.ua/bank/currency"
            logo_url = "https://play-lh.googleusercontent.com/tVdBTQSX3ek05SxDZJClWtohEohC0EHLF7BRqzfq7tRsr3533O" \
                       "NjQxUd-pmQxjGtb2I=w240-h480-rw"
            provider = ExchangeRateProvider.objects.get(name='MonoBank', logo_url=logo_url, api_url=url)
            currency_rates = ExchangeRate.objects.filter(for_date=datetime.today(), provider=provider)
            if currency_rates:
                pass
            else:
                response = requests.get(url)
                bank_data = response.json()
                currency_rate = []
                if ExchangeRateProvider.objects.filter(name='MonoBank', logo_url=logo_url, api_url=url):

                    provider = \
                        ExchangeRateProvider.objects.get(name='MonoBank', logo_url=logo_url, api_url=url)
                    print(provider)
                else:
                    provider = \
                        ExchangeRateProvider.objects.get_or_create(name='MonoBank', logo_url=logo_url, api_url=url)[0]
                    print(provider)

                currency_code_mapping = [
                    '840',
                    '978',
                    '980'
                    # Add more mappings as needed
                ]

                for entry in bank_data:

                    currency_code_a = str(entry['currencyCodeA'])
                    print(response.status_code)
                    # currency_code_b = str(entry['currencyCodeB'])
                    # print(currency_code_b)
                    if currency_code_a not in currency_code_mapping:
                        continue
                    else:
                        actual_date = date.fromtimestamp(entry['date'])
                        currency_a_code = pycountry.currencies.get(numeric=currency_code_a).alpha_3
                        # currency_b_code = pycountry.currencies.get(numeric=currency_code_b).alpha_3
                        if currency_a_code not in self.CURRENCIES:
                            continue
                        else:
                            if ExchangeRate.objects.filter(base_currency='UAH', currency=currency_a_code,
                                                           provider=provider, added_date=datetime.today()).exists():
                                continue

                            else:
                                print(currency_a_code)
                                currency = ExchangeRate(
                                    base_currency='UAH',
                                    currency=currency_a_code,
                                    sale_rate=entry['rateSell'],
                                    buy_rate=entry['rateBuy'],
                                    provider=provider,
                                    added_date=actual_date)

                                currency.save()
                                currency_rate.append(currency)
                                print(response.status_code)

                        print(currency)
                    print(currency_rate)
                    return currency_rate
        except TypeError as e:
            print(f'Error, code will be reloaded because of {e}.')
            self.get_rates_mono()


class ExchangeRatesServiceYear:
    CURRENCIES = ['GBP', 'USD', 'EUR', 'CHF']

    def thread(self):

        end_date = datetime.now()
        start_date = datetime(2023, 1, 1)
        delay = (end_date - start_date).days

        currency_rate = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=settings.MAX_WOKER) as executor:
            futures = [executor.submit(self.get_year_rates, date=start_date + timedelta(days=i)) for i in
                       range(delay + 1)]

            for future in concurrent.futures.as_completed(futures):
                currency_rate.extend(future.result())

    def get_year_rates(self, date):
        url = "https://api.privatbank.ua/p24api/exchange_rates"
        logo_url = "https://avatars.githubusercontent.com/u/95229470?s=280&v=4"
        provider = \
            ExchangeRateProvider.objects.get_or_create(name='PrivatBank', logo_url=logo_url, api_url=url)[0]
        params = {
            'date': date.strftime('%d.%m.%Y')
        }

        response = requests.get(url, params=params)
        data = response.json()

        currency_rate = []
        if 'exchangeRate' in data:
            base_currency = data['baseCurrencyLit']
            rates = data['exchangeRate']
            date = datetime.strptime(data['date'], '%d.%m.%Y').strftime('%Y-%m-%d')
            for r in rates:
                if r['currency'] not in self.CURRENCIES:
                    continue
                else:
                    if ExchangeRate.objects.filter(base_currency=base_currency, currency=r['currency'],
                                                   provider=provider, for_date=date).exists():
                        continue

                    currency = ExchangeRate(
                        base_currency=base_currency,
                        currency=r['currency'],
                        sale_rate=r['saleRate'],
                        buy_rate=r['purchaseRate'],
                        provider=provider,
                        for_date=date
                    )
                    currency.save()

                    currency_rate.append(currency)
            return currency_rate
