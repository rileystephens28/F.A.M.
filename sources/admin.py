from django.contrib import admin
from .models import StockExchange, OptionExchange, CryptoExchange

admin.site.register(StockExchange)
admin.site.register(OptionExchange)
admin.site.register(CryptoExchange)
