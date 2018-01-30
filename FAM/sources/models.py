from django.db import models

class Source(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField()
    last_updated = models.DateTimeField()

    def __str__():
        return name
