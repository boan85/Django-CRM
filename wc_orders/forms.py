from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    action_type = forms.CharField(label='order_action_choices', max_length=100)

    class Meta:
        model = Order
        fields = '__all__'