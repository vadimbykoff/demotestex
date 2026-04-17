from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm
from products.models import Product


def get_user_role(user):
    if not user.is_authenticated:
        return 'guest'
    if user.is_superuser:
        return 'admin'
    if user.groups.filter(name='manager').exists():
        return 'manager'
    if user.groups.filter(name='client').exists():
        return 'client'
    return 'guest'


OrderItemFormSet = inlineformset_factory(
    Order, OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)


@login_required
def order_list(request):
    role = get_user_role(request.user)
    if role == 'guest':
        messages.error(request, 'У вас нет прав для просмотра заказов.')
        return redirect('products:product_list')

    if role in ('admin', 'manager'):
        orders = Order.objects.select_related('customer', 'status', 'pickup_point').all()
    else:
        orders = Order.objects.select_related('customer', 'status', 'pickup_point').filter(customer=request.user)

    return render(request, 'orders/order_list.html', {
        'orders': orders,
        'user_role': role,
    })


@login_required
def order_detail(request, pk):
    role = get_user_role(request.user)
    if role == 'guest':
        messages.error(request, 'У вас нет прав для просмотра заказов.')
        return redirect('products:product_list')

    order = get_object_or_404(Order, pk=pk)

    if role == 'client' and order.customer != request.user:
        messages.error(request, 'У вас нет прав для просмотра этого заказа.')
        return redirect('orders:order_list')

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'user_role': role,
    })


@login_required
def order_create(request):
    role = get_user_role(request.user)
    if role == 'guest':
        messages.error(request, 'У вас нет прав для создания заказов.')
        return redirect('products:product_list')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.save()
            formset.instance = order
            formset.save()
            messages.success(request, f'Заказ #{order.order_number} успешно создан.')
            return redirect('orders:order_list')
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, 'orders/order_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Создать заказ',
        'user_role': role,
    })


@login_required
def order_update(request, pk):
    role = get_user_role(request.user)
    if role not in ('admin', 'manager'):
        messages.error(request, 'У вас нет прав для редактирования заказов.')
        return redirect('orders:order_list')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'Заказ #{order.order_number} успешно обновлён.')
            return redirect('orders:order_list')
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    return render(request, 'orders/order_form.html', {
        'form': form,
        'formset': formset,
        'order': order,
        'title': 'Редактировать заказ',
        'user_role': role,
    })


@login_required
def order_delete(request, pk):
    role = get_user_role(request.user)
    if role not in ('admin', 'manager'):
        messages.error(request, 'У вас нет прав для удаления заказов.')
        return redirect('orders:order_list')

    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        order_number = order.order_number
        order.delete()
        messages.success(request, f'Заказ #{order_number} успешно удалён.')
        return redirect('orders:order_list')

    return render(request, 'orders/order_confirm_delete.html', {
        'order': order,
        'user_role': role,
    })
