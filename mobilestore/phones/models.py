from django.db import models

class Phone(models.Model):
    ''' Information about smartphones. '''
    model = models.CharField(max_length=100, unique=True)
    image = models.ImageField(default='default.png', blank=True)
    manufacturer = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.TextField()
    battery = models.CharField(max_length=200)
    features = models.TextField()
    stock = models.PositiveIntegerField()
    # specs::
    #     body
    #     display
    #     platform
    #     chipset
    #     memory
    # camera::
    #     main
    #     selfie
    #     features

    def __str__(self):
        return self.model
