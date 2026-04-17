from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class OrderStatus(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Статус')

    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказов'

    def __str__(self):
        return self.name


class PickupPoint(models.Model):
    address = models.CharField(max_length=300, unique=True, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Пункт выдачи'
        verbose_name_plural = 'Пункты выдачи'

    def __str__(self):
        return self.address


class Order(models.Model):
    order_number = models.CharField(max_length=50, unique=True, verbose_name='Номер заказа')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    delivery_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата доставки')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Покупатель')
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, verbose_name='Статус')
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.CASCADE, verbose_name='Пункт выдачи')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-order_date']

    def __str__(self):
        return f'Заказ #{self.order_number}'

    def total_price(self):
        return sum(item.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.IntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
        unique_together = ('order', 'product')

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'
