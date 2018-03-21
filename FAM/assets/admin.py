from django.contrib import admin
from .models import Stock, Option, Cryptocurrency

admin.site.register(Stock)
admin.site.register(Option)
admin.site.register(Cryptocurrency)
