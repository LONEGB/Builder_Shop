from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


#customer
class Customer(models.Model):

    customer_id = models.AutoField(verbose_name='Код покупателя', primary_key=True)
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=30, verbose_name='Отчество', null=True, blank=True)
    address = models.CharField(max_length=30, verbose_name='Адрес', null=True, blank=True)
    date_of_birth = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name="Логин", on_delete=models.CASCADE )

    def __str__(self):
        return "{} {}".format(
            self.first_name,
            self.last_name
        )

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


#saler
class Saler(models.Model):

    saler_id = models.AutoField(verbose_name='Код продовца', primary_key=True)
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=30, verbose_name='Отчество', null=True, blank=True)
    address = models.CharField(max_length=30, verbose_name='Адрес', null=True, blank=True)
    date_of_birth = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name="Логин", on_delete=models.CASCADE )

    def __str__(self):
        return "{} {}".format(
            self.first_name,
            self.last_name
        )

    class Meta:
        verbose_name = 'Продавец'
        verbose_name_plural = 'Продавцы'


#sale
class Sale(models.Model):

    sale_id = models.AutoField(verbose_name='Код продажи', primary_key=True)
    date = models.DateField(verbose_name='Дата продажи', default=datetime.now)

    def __str__(self):
        return "{} {}".format(
            self.sale_id,
            self.date
        )

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'


#order
class Order(models.Model):

    order_id = models.AutoField(verbose_name='Код заказа', primary_key=True)
    date = models.DateField(verbose_name='Дата заказа', default=datetime.now)
    discount = models.PositiveIntegerField(verbose_name = 'Скидка', null=True, blank=True)
    sale = models.ForeignKey(Sale, verbose_name='Код продажи',  null=True, blank=True, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, verbose_name='Покупатель', on_delete=models.CASCADE)
    delivery = models.FloatField(verbose_name='Стоимость доставки', default=1000)
    total_price = models.FloatField(verbose_name='Стоимость заказа', default='OrderMaterial.material.price*OrderMaterial.quantity')
    status = models.CharField(
        verbose_name='Статус заказа',
        max_length=14,
        choices=[('В обработке', 'В обработке'), ('Выполнен', 'Выполнен')],
        default='В обработке'
    )


    def __str__(self):
        return "{} {}".format(
            self.order_id,
            self.date
        )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


#manual_measurements
class Manual_measurements(models.Model):

    measure_id = models.AutoField(verbose_name='Код единицы измерения', primary_key=True)
    measure = models.CharField(max_length=30, verbose_name='Единица измерения')


    def __str__(self):
        return "{}".format(
            self.measure
        )

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'


#material_category
class Material_category(models.Model):

    category_id = models.AutoField(verbose_name='Код категории', primary_key=True)
    name = models.CharField(max_length=30, verbose_name='Наименование категории')

    def __str__(self):
        return "{}".format(
            self.name,
        )

    class Meta:
        verbose_name = 'Категория стройматериала'
        verbose_name_plural = 'Категории стройматериала'

    def get_absolute_url(self):
        return reverse('builder:product_list_by_category')


#material
class Material(models.Model):

    material_id = models.AutoField(verbose_name='Код стройматериала', primary_key=True)
    name = models.CharField(max_length=30, verbose_name='Наименование стройматериала')
    weight = models.FloatField(verbose_name='Вес', null=True, blank=True)
    measure = models.ForeignKey(Manual_measurements, verbose_name='Единица измерения', on_delete=models.CASCADE)
    volume = models.FloatField(verbose_name='Объем', null=True, blank=True)
    length = models.FloatField(verbose_name='Длина', null=True, blank=True)
    width = models.FloatField(verbose_name='Ширина', null=True, blank=True)
    height = models.FloatField(verbose_name='Высота', null=True, blank=True)
    category = models.ForeignKey(Material_category, related_name='products', verbose_name='Категория стройматериала', on_delete=models.CASCADE)
    price = models.FloatField(max_length=30, verbose_name='Цена за единицу')
    image = models.ImageField(upload_to='product/%Y/%m/%d', null=True, blank=True, default='product/no_image.png')

    def __str__(self):
        return "{}".format(
            self.name
        )

    class Meta:
        verbose_name = 'Стройматериал'
        verbose_name_plural = 'Стройматериалы'

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id])


#order_material
class OrderMaterial(models.Model):

    order = models.ForeignKey(Order, verbose_name='Номер заказа', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name='Номер стройматериала', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return "{} {} {}".format(
            self.order,
            self.material,
            self.quantity
        )

    class Meta:
        verbose_name = 'Корзина заказа'
        verbose_name_plural = 'Корзины заказа'


