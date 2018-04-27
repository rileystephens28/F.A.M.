from django.contrib import admin
from .models import StockInvestment, OptionInvestment, CryptoInvestment, Account

admin.site.register(StockInvestment)
admin.site.register(OptionInvestment)
admin.site.register(CryptoInvestment)
admin.site.register(Account)
