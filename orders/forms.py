from django import forms
from .models import Order, OrderItem, OrderStatus, PickupPoint


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_number', 'status', 'pickup_point', 'delivery_date']
        widgets = {
            'order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'pickup_point': forms.Select(attrs={'class': 'form-select'}),
            'delivery_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }
