from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/register/', views.register, name='register'),
    path('register_info/', views.register_info, name='register_info'),
    path('catalog/<str:category>/', views.product_list, name='product_list'),
    path('catalog/', views.product_list, name='product_list'),
    path('detail/<material_id>/', views.product_detail, name='product_detail'),
    path('create/<customer_id>/', views.order_create, name='order_create'),
    path('orders/', views.orders_list, name='orders_list'),
    path('update_status/<int:order_id>/',views.update_view_status,name='update_view_status'),
    path('order_details/', views.searh, name='searh'),
    path('searh2/', views.searh2, name='searh2'),
    path('reports/', views.reports, name='reports'),
    path('reports2/', views.reports2, name='reports2'),
    path('reports_1/', views.reports_1, name='reports_1'),
    path('reports_2/', views.reports_2, name='reports_2'),
    path('reports_3/', views.reports_3, name='reports_3'),
    path('graph/', views.graph, name='graph'),
    path('add_category/', views.add_category, name='add_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('add_material/', views.add_material, name='add_material'),
    path('delete_material/<int:material_id>/', views.delete_material, name='delete_material'),
    path('update_material/<int:material_id>/', views.update_material, name='update_material'),
    path('measure_list/', views.measure_list, name='measure_list'),
    path('delete_measure/<int:measure_id>', views.delete_measure, name='delete_measure'),
]

