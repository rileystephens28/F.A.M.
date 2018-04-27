from django.db import models

class StockExchange(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class OptionExchange(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class CryptoExchange(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
