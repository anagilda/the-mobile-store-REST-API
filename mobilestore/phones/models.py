from django.db import models

class Phone(models.Model):
    ''' Information about smartphones. '''
    model = models.CharField(max_length=100, unique=True)
    image = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    manufacturer = models.CharField(max_length=100, unique=True)
    description = models.TextField()
        
