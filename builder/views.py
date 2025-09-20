import calendar
import json
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseRedirect, FileResponse, HttpResponse
from cart.cart import Cart
from cart.forms import CartAddProductForm
from builder.forms import UserRegistrationForm, ProfileForm, OrderCreateForm, MaterialCreateForm, MeasureCreateForm, \
    MaterialUpdateForm
from django.db.models import Sum
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from .models import Customer, Material, Material_category, OrderMaterial, Order, Sale, Manual_measurements


def index(request):
    if request.user.is_anonymous:
        return render(
            request,
            'index.html',
        )
    else:
        profile_exist = Customer.objects.filter(user=request.user).exists()
        if not profile_exist:
            return redirect('register_info')
        else:
            return render(
                request,
                'index.html',
            )


def login(request):
    return render(
        request,
        'registration/login.html',
    )


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password1'])
            # Save the User object
            new_user.save()
            new_user.groups.add(Group.objects.get(name="customer"))
            return render(request, 'registration/register_done.html')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})


def register_info(request):
    if request.method == 'POST':
        user_form = ProfileForm(request.POST)
        user = request.user
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            new_user.user = user
            new_user.first_name = user.first_name
            new_user.last_name = user.last_name
            # Save the User object
            new_user.save()
            return render(request, 'registration/register_info_done.html')
    else:
        user_form = ProfileForm()
    return render(request, 'registration/register_info.html', {'user_form': user_form})


def product_list(request, category='all'):
    categories = Material_category.objects.all()
    if category == 'all':
        products = Material.objects.all()
    else:
        products = Material.objects.filter(category__name=category)
    return render(request, 'catalog.html',
                  {
                      'category': category,
                      'categories': categories,
                      'products': products
                  })


def product_detail(request, material_id):
    product = get_object_or_404(Material, material_id=material_id)
    cart_product_form = CartAddProductForm()
    return render(request, 'detail.html', {'product': product,
                                           'cart_product_form': cart_product_form})


def order_create(request, customer_id):
    cart = Cart(request)
    customer = Customer.objects.filter(customer_id=customer_id).first()
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.total_price = cart.get_total_price()
            order.save()
            for item in cart:
                OrderMaterial.objects.create(order=order,
                                             material=item['product'],
                                             quantity=item['quantity'])
            # очистка корзины

            cart.clear()
            return render(request, 'created.html',
                          {'order': order})
    else:
        form = OrderCreateForm
    return render(request, 'create.html',
                  {'cart': cart, 'form': form})


def orders_list(request):
    filter = request.GET.get('filter', '')
    if filter:
        orders = Order.objects.all().order_by(filter)
    else:
        orders = Order.objects.all().order_by('date')
    return render(request, 'orders.html', {'orders': orders})


def update_view_status(request, order_id):
    try:
        customer_order = Order.objects.get(order_id=order_id)
        if request.method == "POST":
            customer_order.status = request.POST.get("status")
            if request.POST.get("status") == 'Выполнен':
                customer_sale = Sale.objects.create()
                customer_sale.date = customer_order.date
                customer_sale.save()
                customer_order.sale = customer_sale
                customer_order.save()
            else:
                customer_sale = customer_order.sale
                customer_order.sale = None
                customer_order.save()
                customer_sale.delete()
            return HttpResponseRedirect("/builder/orders/")
        else:
            context = {
                "customer_order": customer_order
            }
            return render(request, "update_status.html", context)
    except Order.DoesNotExist:
        return HttpResponseNotFound("<h2>Заказ не найден</h2>")


def searh(request):
    if request.method == 'POST' and request.POST['search'] == 'True':
        last_name = request.POST['last_name']
        category = request.POST['category']
        quantity = request.POST['quantity']
        date_from = request.POST['date_from']
        if last_name != '' and category != '' and quantity !='' and date_from != '':
            ordermat = OrderMaterial.objects.filter(order__customer__last_name__contains=last_name,
                                                    material__category__name__contains=category, quantity__contains=quantity, order__date=date_from)
        elif category != '' and quantity !='' and date_from != '':
            ordermat = OrderMaterial.objects.filter(material__category__name__contains=category,
                                                    quantity__contains=quantity, order__date=date_from)
        elif last_name != '' and category != '' and quantity != '':
            ordermat = OrderMaterial.objects.filter(order__customer__last_name__contains=last_name, material__category__name__contains=category,
                                                    quantity__contains=quantity)
        elif last_name != '' and quantity != '' and date_from != '':
            ordermat = OrderMaterial.objects.filter(order__customer__last_name__contains=last_name,
                                                    quantity__contains=quantity,order__date=date_from)
        elif last_name != '' and quantity != '':
            ordermat = OrderMaterial.objects.filter(order__customer__last_name__contains=last_name,
                                                    quantity__contains=quantity)
        elif category != '' and quantity != '':
            ordermat = OrderMaterial.objects.filter(material__category__name__contains=category,
                                                    quantity__contains=quantity)
        elif quantity != '' and date_from != '':
            ordermat = OrderMaterial.objects.filter(quantity__contains=quantity, order__date=date_from)
        elif quantity != '':
            ordermat = OrderMaterial.objects.filter(quantity__contains=quantity)
        elif last_name != ''  and quantity != '' and date_from != '':
            ordermat = OrderMaterial.objects.filter(order__customer__last_name__contains=last_name,
                                                    quantity__contains=quantity, order__date=date_from)
        elif last_name != '' and category != '' and date_from != '':
            ordermat = OrderMaterial.objects.filter(order__customer__last_name__contains=last_name,
                                                    material__category__name__contains=category, order__date=date_from)
        elif last_name != '' and category != '':
            ordermat = OrderMaterial.objects.filter(order__customer__last_name__contains=last_name, material__category__name__contains=category)
        elif last_name != '' and date_from != '':
            ordermat = OrderMaterial.objects.filter(order__customer__last_name__contains=last_name, order__date=date_from)
        elif last_name != '':
            ordermat = OrderMaterial.objects.filter(order__customer__last_name__contains=last_name)
        elif category != '' and date_from != '':
            ordermat = OrderMaterial.objects.filter(material__category__name__contains=category, order__date=date_from)
        elif category != '':
            ordermat = OrderMaterial.objects.filter(material__category__name__contains=category)
        elif date_from != '':
            ordermat = OrderMaterial.objects.filter(order__date=date_from)
        else:
            ordermat = OrderMaterial.objects.all()
        context = {
            'date_from': date_from,
            'last_name': last_name,
            'ordermat': ordermat,
            'category': category,
        }
        return render(request, 'order_details.html', context=context)
    customers = Customer.objects.all()
    ordermat = OrderMaterial.objects.all()
    context = {
        'customers': customers,
        'ordermat': ordermat,
    }
    return render(request, 'order_details.html', context=context)


def reports_1(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    data = []
    order_products = OrderMaterial.objects \
        .values('order__order_id',
                 'order__date',
                 'order__customer__last_name',
                 'order__customer__first_name',
                 'order__customer__patronymic',
                 'material__category__name',
                 'material__name',
                 'material__price',
                 'quantity',
                 'order__delivery',
                 'order__total_price'
                ) \
        .all().order_by('order__date','order__customer__last_name')
    data.append((
        'ID заказа',
        'Дата заказа',
        'ФИО заказчика',
        'Категория',
        'Наименование',
        'Цена',
        'Количество',
        'Доставка',
        'Общая стоимость'
    ))
    for order_product in order_products:
        data.append((
            order_product['order__order_id'],
            str(order_product['order__date'].strftime("%d-%m-%Y")),
            str(order_product['order__customer__last_name'])
            + ' ' + str(order_product['order__customer__first_name']).upper()[0]
            + '.' + str(order_product['order__customer__patronymic']).upper()[0]+ '.',
            order_product['material__category__name'],
            order_product['material__name'][:10] + '...',
            order_product['material__price'],
            order_product['quantity'],
            order_product['order__delivery'],
            order_product['order__total_price']+order_product['order__delivery']
        ))
    pdfmetrics.registerFont(TTFont('Roboto', 'Roboto-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('RobotoBold', 'Roboto-Bold.ttf'))
    t = Table(data, 9 * [0.93 * inch], len(data) * [0.5 * inch])
    t.setStyle(TableStyle([('FONT', (0, 0), (-1, 0), 'RobotoBold'),
                           ('FONTSIZE', (0, 0), (-1, -1), 9),
                           ('FONT', (0, 1), (-1, -1), 'Roboto'),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                           ('INNERGRID', (0, 1), (-1, -1), 0.5, colors.black),
                           ('BOX', (0, 1), (-1, -1), 0.25, colors.black),
                           ]))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='RobotoTitle', alignment=TA_CENTER, fontName='Roboto', fontSize=14, ))
    styles.add(ParagraphStyle(name='RobotoEnd', alignment=TA_RIGHT, fontName='RobotoBold', fontSize=14, wordWrap=True))

    elements.append(Paragraph('Отчет по заказам ', styles['RobotoTitle']))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='orders.pdf')


def reports(request):
    return render(request,'reports.html',
    )


def reports2(request):
    return render(request,'reports2.html',
    )


def reports_2(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    data = []

    order_products = OrderMaterial.objects \
        .values('order__order_id',
                 'order__customer__last_name',
                 'order__customer__first_name',
                 'order__customer__patronymic',
                 'quantity',
                 'order__total_price'
                ) \
        .filter(order__customer=request.user.customer)
    sum2 = list(OrderMaterial.objects.filter(order__customer=request.user.customer).aggregate(Sum('quantity')).values())[0]
    data.append((
        'ID заказа',
        'ФИО заказчика',
        'Количество',
        'Общая стоимость'
    ))
    for order_product in order_products:
        data.append((
            order_product['order__order_id'],
            str(order_product['order__customer__last_name'])
            + ' ' + str(order_product['order__customer__first_name']).upper()[0]
            + '.' + str(order_product['order__customer__patronymic']).upper()[0]+ '.',
            order_product['quantity'],
            order_product['order__total_price']
        ))
    pdfmetrics.registerFont(TTFont('Roboto', 'Roboto-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('RobotoBold', 'Roboto-Bold.ttf'))
    t = Table(data, 9 * [1.5 * inch], len(data) * [0.5 * inch])
    t.setStyle(TableStyle([('FONT', (0, 0), (-1, 0), 'RobotoBold'),
                           ('FONTSIZE', (0, 0), (-1, -1), 9),
                           ('FONT', (0, 1), (-1, -1), 'Roboto'),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                           ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                           ('INNERGRID', (0, 1), (-1, -1), 0.5, colors.black),
                           ('BOX', (0, 1), (-1, -1), 0.25, colors.black),
                           ]))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='RobotoTitle', alignment=TA_CENTER, fontName='Roboto', fontSize=14, ))
    styles.add(ParagraphStyle(name='RobotoEnd', alignment=TA_RIGHT, fontName='RobotoBold', fontSize=14, wordWrap=True))

    elements.append(Paragraph('Накладная заказов №2 ', styles['RobotoTitle']))
    elements.append(t)

    customer = Customer.objects.values('last_name') \
        .filter(pk=request.user.customer.customer_id) \
        .annotate(sum=Sum('order__total_price'))
    s = ''
    for cl in customer:
        s = cl['sum']
    elements.append(Paragraph('Итог: сумма - ' + str(s), styles['RobotoEnd']))
    elements.append(Paragraph('Всего товаров:' + str(sum2), styles['RobotoEnd']))
    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='orders.pdf')


def reports_3(request):
    if request.method == 'POST' and request.POST['search'] == 'True':
        year = request.POST.get('year')
        category = request.POST['category']
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        data = []
        if category != '' and year != '':
            order_products = OrderMaterial.objects \
            .values('order__sale__sale_id',
                     'material__name',
                     'quantity',
                     'order__total_price'
                    ) \
            .filter(order__date__month=year, material__category__name=category).order_by('order__date','material__category__name','material__name')
        elif category != '':
            order_products = OrderMaterial.objects \
            .values('order__sale__sale_id',
                     'material__name',
                     'quantity',
                     'order__total_price'
                    ) \
            .filter(material__category__name=category).order_by('order__date','material__category__name','material__name')
        elif year != '':
            order_products = OrderMaterial.objects \
            .values('order__sale__sale_id',
                     'material__name',
                     'quantity',
                     'order__total_price'
                    ) \
            .filter(order__date__month=year).order_by('order__date','material__category__name','material__name')
        else:
            order_products = OrderMaterial.objects \
                .values('order__sale__sale_id',
                        'material__name',
                        'quantity',
                        'order__total_price'
                        ) \
                .all().order_by('order__date', 'material__category__name', 'material__name')
        data.append((
            'ID продажи',
            'Наименования материала',
            'Количество',
            'Общая стоимость'
        ))
        for order_product in order_products:
            data.append((
                order_product['order__sale__sale_id'],
                order_product['material__name'][:10] + '...',
                order_product['quantity'],
                order_product['order__total_price']
            ))
        pdfmetrics.registerFont(TTFont('Roboto', 'Roboto-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('RobotoBold', 'Roboto-Bold.ttf'))
        t = Table(data, 9 * [2 * inch], len(data) * [0.5 * inch])
        t.setStyle(TableStyle([('FONT', (0, 0), (-1, 0), 'RobotoBold'),
                               ('FONTSIZE', (0, 0), (-1, -1), 9),
                               ('FONT', (0, 1), (-1, -1), 'Roboto'),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                               ('INNERGRID', (0, 1), (-1, -1), 0.5, colors.black),
                               ('BOX', (0, 1), (-1, -1), 0.25, colors.black),
                               ]))
        if category != '' and year != '':
            sum2 = list(
                OrderMaterial.objects.filter(order__date__month=year, material__category__name=category).aggregate(
                    Sum('order__total_price')).values())[0]
        elif category !='':
            sum2 = list(OrderMaterial.objects.filter(material__category__name=category).aggregate(
                Sum('order__total_price')).values())[0]
        elif year != '':
            sum2 = list(OrderMaterial.objects.filter(order__date__month=year).aggregate(
                Sum('order__total_price')).values())[0]
        else:
            sum2 = list(OrderMaterial.objects.all().aggregate(Sum('order__total_price')).values())[0]
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RobotoTitle', alignment=TA_CENTER, fontName='Roboto', fontSize=14))
        styles.add(ParagraphStyle(name='RobotoEnd', alignment=TA_RIGHT, fontName='RobotoBold', fontSize=14))

        elements.append(Paragraph('Отчет по продажам ', styles['RobotoTitle']))
        elements.append(Paragraph('Месяц №' + str(year), styles['RobotoTitle']))
        elements.append(Paragraph('Категория материалов: ' + str(category), styles['RobotoTitle']))
        elements.append(t)
        elements.append(Paragraph('Итог: сумма - ' + str(sum2), styles['RobotoEnd']))
        doc.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='orders.pdf')
    return render(request, 'reports3.html')


def searh2(request):
    if request.method == 'POST' and request.POST['search'] == 'True':
        year = request.POST.get('year')
        category = request.POST['category']
        if category != '' and year != '':
            ordermat = OrderMaterial.objects.filter(material__category__name__contains=category, order__date__month=year)
        elif category != '':
            ordermat = OrderMaterial.objects.filter(material__category__name__contains=category)
        elif year != '':
            ordermat = OrderMaterial.objects.filter(order__date__month=year)
        else:
            ordermat = OrderMaterial.objects.all()
        context = {
            'year': year,
            'ordermat': ordermat,
            'category': category,
        }
        return render(request, 'reports3.html', context=context)
    customers = Customer.objects.all()
    ordermat = OrderMaterial.objects.all()
    context = {
        'customers': customers,
        'ordermat': ordermat,
    }
    return render(request, 'reports3.html', context=context)


def graph(request):
    year = request.POST.get('year')
    if year == None:
        categories = Order.objects.values(
            'ordermaterial__material__category',
            'ordermaterial__material__category__name',
            'ordermaterial__quantity',
            'ordermaterial__material__price',
            'date') \
            .filter(
            date__month__gte=int(datetime.datetime.now().strftime("%m")),
            date__month__lte=int(datetime.datetime.now().strftime("%m")) + 1
                    )\
            .order_by('-ordermaterial__material__category__name')
        days = calendar.monthrange(int(datetime.datetime.now().strftime("%Y")),
                                   int(datetime.datetime.now().strftime("%m")))[1]
    else:
        categories = Order.objects.values(
            'ordermaterial__material__category',
            'ordermaterial__material__category__name',
            'ordermaterial__quantity',
            'ordermaterial__material__price',
            'date') \
            .filter(
            date__month__gte=str(int(year)),
            date__month__lte=str(int(year) + 1)
        ) \
            .order_by('-ordermaterial__material__category__name')
        days = calendar.monthrange(int(year), int(year))[1]
    days_arr = []
    for i in range(1, days + 1, 1):
        days_arr.append(0)
    category_sum = []
    category_arr = []
    for category in categories:
        cat = Material_category.objects.get(pk=category['ordermaterial__material__category'])
        date_order = str(category['date']).split('-')[2]
        if date_order[0] == '0':
            date_order = date_order[1]

        if category_arr != [] and category_arr[-1]['name'] == str(cat.name):
            category_arr[-1]['data'][int(date_order) - 1] += 1
        else:
            category_arr.append({'name': str(cat.name), 'data': days_arr.copy()})
            category_arr[-1]['data'][int(date_order) - 1] += 1

    days_arr = []
    for i in range(1, days + 1, 1):
        days_arr.append(i)

    charts_data = json.dumps(category_arr)
    charts_categories = json.dumps(days_arr)
    context = {
        'Material_category': category_sum,
        'charts_data': charts_data,
        'charts_categories': charts_categories,
    }
    return render(request, 'graph.html', context=context)


def add_category(request, category='all'):
    categories = Material_category.objects.all()
    if request.method == 'POST':
        cat_name = request.POST['category']
        if cat_name != '':
            category_name = Material_category.objects.create(name=cat_name)
            category_name.save()
        else:
            return HttpResponse("Введите название категории!")
    if category == 'all':
        products = Material.objects.all()
    else:
        products = Material.objects.filter(category__name=category)
    return render(request, 'catalog.html',
                  {
                      'category': category,
                      'categories': categories,
                      'products': products
                  })


def delete_category(request, category_id):
    Material_category.objects.get(category_id=category_id).delete()
    return redirect('product_list')


def add_material(request):
    if request.method == 'POST':
        form = MaterialCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            redirect('product_list')
    else:
        form = MaterialCreateForm()
    return render(request,'add_material.html', {'form': form})


def delete_material(request, material_id):
    Material.objects.get(material_id=material_id).delete()
    return redirect('product_list')

def update_material(request, material_id):
    try:
        mat = Material.objects.get(material_id=material_id)
        if request.method == "POST":
            form = MaterialUpdateForm(request.POST, request.FILES)
            if form.is_valid():
                form.save(update_fields=mat.name)
                redirect('product_list')
                # mat.name = request.POST.get("name")
                # mat.weight = request.POST.get("weight")
                # mat.Manual_measurements = request.POST.get("measure")
                # mat.volume = request.POST.get("volume")
                # mat.length = request.POST.get("length")
                # mat.width = request.POST.get("width")
                # mat.height = request.POST.get("height")
                # mat.Material_category = request.POST.get("category")
                # mat.price = request.POST.get("price")
                # mat.image = request.FILES
                # mat.save()
            return HttpResponseRedirect("/")
        else:
            return render(request, "update_material.html", {"mat": mat})
    except Material.DoesNotExist:
        return HttpResponseNotFound("<h2>Такого товара нет!</h2>")





# def update_material1(request):
#     if request.method == 'POST':
#         form = MaterialUpdateForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save(update_fields=["name","weight", "measure", "volume", "length", "width", "height", "category", "price", "image"])
#             redirect('product_list')
#     else:
#         form = MaterialUpdateForm()
#     return render(request,'update_material.html', {'form': form})

def measure_list(request):
    measuries = Manual_measurements.objects.all()
    if request.method == 'POST':
        form = MeasureCreateForm(request.POST)
        if form.is_valid():
            form.save()
            redirect('measure_list')
    else:
        form = MeasureCreateForm()
    return render(request, 'measure.html',
                  {
                      'measuries': measuries,
                      'form': form
                  })


def delete_measure(request, measure_id):
    Manual_measurements.objects.get(measure_id=measure_id).delete()
    return redirect('measure_list')