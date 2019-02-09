from django.db import models
from django.contrib.postgres.fields import JSONField

class Phone(models.Model):
    ''' Information about smartphones. '''
    model = models.CharField(max_length=100, unique=True)
    image = models.ImageField(default='default.png', blank=True)
    manufacturer = models.ForeignKey('Company', on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.TextField()
    specs = JSONField()
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.model


class Company(models.Model):
    ''' Information about companies. '''
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name