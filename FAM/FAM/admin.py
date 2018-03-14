from django.contrib import admin
from cryptocurrencies.models import Cryptocurrency
from sources.models import CryptoExchange
from sources.models import StockExchange, OptionExchange
from options.models import Option
from stocks.models import Stock

admin.site.register(CryptoExchange)
admin.site.register(StockExchange)
admin.site.register(OptionExchange)
admin.site.register(Cryptocurrency)
admin.site.register(Stock)
admin.site.register(Option)
