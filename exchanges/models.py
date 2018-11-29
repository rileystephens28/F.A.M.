from django.db import models

class Exchange(models.Model):
    """ DB model that represents an exchange  """

    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
