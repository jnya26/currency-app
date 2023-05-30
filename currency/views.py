import json

from datetime import datetime
from dateutil.utils import today
from django.http import HttpResponse
from django.shortcuts import render
from decimal import Decimal
from currency.forms import Calculator
from currency.services import ExchangeRatesServices, ExchangeRatesServicesMono, ExchangeRatesServiceYear
from .models import ExchangeRate, ExchangeRateProvider


def privat(request):
    service = ExchangeRatesServices()
    rates = service.get_rates()
    form = Calculator(request.POST)
    if request.method == "POST":
        first_value = Decimal(form.data['first_value'])

        exchange_rate_providers = ExchangeRateProvider.objects.filter(name='PrivatBank',
                                                                      api_url="https://api.privatbank.ua/p24api/"
                                                                              "pubinfo?exchange&coursid=5")

        if exchange_rate_providers.exists():
            exchange_rate_provider = exchange_rate_providers.first()
            exchange_rate = ExchangeRate.objects.filter(currency=form.data['currency_name_privat'],
                                                        provider=exchange_rate_provider).order_by('for_date').first()

            if exchange_rate:
                buy_rate = exchange_rate.buy_rate
                sell_rate = exchange_rate.sale_rate
                provider = exchange_rate.provider.name
                logo_url = exchange_rate.provider.logo_url
                added_date = exchange_rate.added_date
                from_ua_value = first_value / sell_rate
                to_ua_value = first_value * buy_rate

                context = {
                    'rates': rates,
                    'form': form,
                    'from_ua_value': from_ua_value,
                    'exchange_rate': exchange_rate,
                    'buy_rate': buy_rate,
                    'sell_rate': sell_rate,
                    'provider': provider,
                    'logo_url': logo_url,
                    'added_date': added_date,
                    'to_ua_value': to_ua_value
                }
                return render(request, 'core/index.html', context)

    else:
        form = Calculator()

    context = {
        'rates': rates,
        'form': form,
    }
    return render(request, 'core/index.html', context)


# {'mono_rates': mono_rates}

def mono(request):
    service = ExchangeRatesServicesMono()
    rates = service.get_rates_mono()
    form = Calculator(request.POST)
    if request.method == "POST":
        first_value = Decimal(form.data['first_value'])

        exchange_rate_providers = ExchangeRateProvider.objects.filter(name='MonoBank')

        if exchange_rate_providers.exists():
            exchange_rate_provider = exchange_rate_providers.first()
            exchange_rate = ExchangeRate.objects.filter(currency=form.data['currency_name_privat'],
                                                        provider=exchange_rate_provider).order_by('added_date').first()

            if exchange_rate:
                buy_rate = exchange_rate.buy_rate
                sell_rate = exchange_rate.sale_rate
                provider = exchange_rate.provider.name
                logo_url = exchange_rate.provider.logo_url
                added_date = exchange_rate.added_date
                from_ua_value = first_value / sell_rate
                to_ua_value = first_value * buy_rate

                context = {
                    'rates': rates,
                    'form': form,
                    'from_ua_value': from_ua_value,
                    'exchange_rate': exchange_rate,
                    'buy_rate': buy_rate,
                    'sell_rate': sell_rate,
                    'provider': provider,
                    'logo_url': logo_url,
                    'added_date': added_date,
                    'to_ua_value': to_ua_value
                }

                return render(request, 'core/index.html', context)

    else:
        form = Calculator()

    context = {
        'rates': rates,
        'form': form,
    }
    return render(request, 'core/index.html', context)


def privat_year(request):
    start_date = today()
    end_date = datetime(2023, 1, 1)
    delay = (start_date - end_date).days
    print(delay)
    provider = ExchangeRateProvider.objects.filter(name="PrivatBank",
                                                   api_url="https://api.privatbank.ua/p24api/exchange_rates").first()
    counts = ExchangeRate.objects.filter(provider_id=provider).count()
    print(counts)
    if counts < delay * 4:
        service = ExchangeRatesServiceYear()
        service.thread()

    exchange_rates_provider = ExchangeRateProvider.objects.filter(name="PrivatBank",
                                                                  api_url="https://api.privatbank.ua/p24api/"
                                                                          "exchange_rates")
    form = Calculator(request.POST)
    if exchange_rates_provider.exists():
        exchange_rate_provider = exchange_rates_provider.first()
        exchange_rates = ExchangeRate.objects.filter(base_currency="UAH", currency__in=['USD', 'EUR', 'CHF', 'GBP'],
                                                     provider=exchange_rate_provider).order_by('for_date').all()

        if exchange_rates:
            currency_data_US = ExchangeRate.objects.filter(for_date__gte='2023-01-01', for_date__lte=today(),
                                                           currency__in=['USD']).order_by('for_date')
            currency_data_json_US = json.dumps([{
                'for_date': rate.for_date.strftime('%Y-%m-%d'),
                'buy_rate': float(rate.buy_rate),
                'currency': rate.currency,
                # Include other fields as needed
            } for rate in currency_data_US])

            currency_data_EUR = ExchangeRate.objects.filter(for_date__gte='2023-01-01', for_date__lte=today(),
                                                            currency__in=['EUR']).order_by('for_date')
            currency_data_json_EUR = json.dumps([{
                'for_date': rate.for_date.strftime('%Y-%m-%d'),
                'buy_rate': float(rate.buy_rate),
                'currency': rate.currency,
                # Include other fields as needed
            } for rate in currency_data_EUR])

            currency_data_CHF = ExchangeRate.objects.filter(for_date__gte='2023-01-01', for_date__lte=today(),
                                                            currency__in=['CHF']).order_by('for_date')
            currency_data_json_CHF = json.dumps([{
                'for_date': rate.for_date.strftime('%Y-%m-%d'),
                'buy_rate': float(rate.buy_rate),
                'currency': rate.currency,
                # Include other fields as needed
            } for rate in currency_data_CHF])

            currency_data_GBP = ExchangeRate.objects.filter(for_date__gte='2023-01-01', for_date__lte=today(),
                                                            currency__in=['GBP']).order_by('for_date')
            currency_data_json_GBP = json.dumps([{
                'for_date': rate.for_date.strftime('%Y-%m-%d'),
                'buy_rate': float(rate.buy_rate),
                'currency': rate.currency,
                # Include other fields as needed
            } for rate in currency_data_GBP])

            context = {
                'currency_data_US': currency_data_json_US,
                'currency_data_EUR': currency_data_json_EUR,
                'currency_data_GBP': currency_data_json_GBP,
                'currency_data_CHF': currency_data_json_CHF,
                'form': form
            }

            html_content = render(request, 'core/index.html', context)
            return HttpResponse(html_content)
