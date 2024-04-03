from django.contrib import admin
from .models import UserProfile, Order, Medication, Invoice, Payment

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Order)
admin.site.register(Medication)
admin.site.register(Invoice)
admin.site.register(Payment)
# admin.site.register(Category)