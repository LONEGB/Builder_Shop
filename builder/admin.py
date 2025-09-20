from django.contrib import admin
from . import models
# Register your models here.


admin.site.register(models.Customer)
admin.site.register(models.Saler)
admin.site.register(models.Order)
admin.site.register(models.Material)
admin.site.register(models.Material_category)
admin.site.register(models.Manual_measurements)
admin.site.register(models.Sale)
admin.site.register(models.OrderMaterial)