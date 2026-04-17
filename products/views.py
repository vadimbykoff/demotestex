from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Supplier
from .forms import ProductForm


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

# /products?search="test user"
def product_list(request):
    """Список электрозапчастей с учетом роли пользователя"""
    user_role = get_user_role(request.user) if request.user.is_authenticated else 'guest'

    # Базовый queryset
    products = Product.objects.select_related('category', 'manufacturer', 'supplier', 'unit')

    # Фильтры и поиск доступны только администратору
    if user_role == 'admin':
        # Поиск
        search_query = request.GET.get('search', '')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(manufacturer__name__icontains=search_query) |
                Q(supplier__name__icontains=search_query) |
                Q(unit__name__icontains=search_query)
            )

        # Фильтр по поставщику
        supplier_filter = request.GET.get('supplier', '')
        if supplier_filter:
            products = products.filter(supplier__id=supplier_filter)

        # Сортировка
        sort_by = request.GET.get('sort', 'name')
        if sort_by == 'quantity_asc':
            products = products.order_by('quantity')
        elif sort_by == 'quantity_desc':
            products = products.order_by('-quantity')
        else:
            products = products.order_by('name')

        suppliers = Supplier.objects.all()
    else:
        suppliers = None
        search_query = ''
        supplier_filter = ''
        sort_by = 'name'

    if user_role != 'admin':
        products = products.order_by('name')

    # Пагинация
    paginator = Paginator(products, 10)  # 10 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'user_role': user_role,
        'suppliers': suppliers,
        'search_query': search_query,
        'supplier_filter': supplier_filter,
        'sort_by': sort_by,
    }

    return render(request, 'products/product_list.html', context)


@login_required
def product_create(request):
    """Создание новой электрозапчасти (только для администраторов)"""
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для выполнения этого действия.')
        return redirect('products:product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Электрозапчасть успешно создана.')
            return redirect('products:product_list')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Добавить электрозапчасть',
        'user_role': get_user_role(request.user)
    })


@login_required
def product_update(request, pk):
    """Редактирование электрозапчасти (только для администраторов)"""
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для выполнения этого действия.')
        return redirect('products:product_list')

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Удаляем старое изображение, если оно заменено
            if 'image' in request.FILES and product.image:
                product.image.delete()
            form.save()
            messages.success(request, 'Электрозапчасть успешно обновлена.')
            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {
        'form': form,
        'product': product,
        'title': 'Редактировать электрозапчасть',
        'user_role': get_user_role(request.user)
    })


@login_required
def product_delete(request, pk):
    """Удаление электрозапчасти (только для администраторов)"""
    if not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для выполнения этого действия.')
        return redirect('products:product_list')

    product = get_object_or_404(Product, pk=pk)

    # Проверка связи с заказами отключена, так как модуль заказов удален из стартовой версии.

    if request.method == 'POST':
        # Удаляем изображение
        if product.image:
            product.image.delete()
        product.delete()
        messages.success(request, 'Электрозапчасть успешно удалена.')
        return redirect('products:product_list')

    return render(request, 'products/product_confirm_delete.html', {
        'product': product,
        'user_role': get_user_role(request.user)
    })
