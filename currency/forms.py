from django import forms


class Calculator(forms.Form):
    CURRENCY_CHOICES = [
        ('CHF', 'CHF'),
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('EUR', 'EUR'),
        # Add more currency options if needed
    ]
    CURRENCY_CHOICES_PRIVAT = [
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        # Add more currency options if needed
    ]

    first_value = forms.CharField(widget=forms.TextInput(attrs={'class': 'left_value_amount'}), label='Enter value',
                                  validators=[], max_length=30)
    second_value = forms.DecimalField(max_digits=10, decimal_places=4)
    currency_name_privat = forms.ChoiceField(label='Currency', choices=CURRENCY_CHOICES_PRIVAT,
                                             widget=forms.Select(attrs={'class': 'dropdown'}))
    currency_name = forms.ChoiceField(label='Currency', choices=CURRENCY_CHOICES,
                                      widget=forms.Select(attrs={'class': 'dropdown'}))

    currency_value = forms.DecimalField(max_digits=10, decimal_places=4)
