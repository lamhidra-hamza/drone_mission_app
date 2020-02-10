from django.db import models

# Create your models here.

class Vehicle(models.Model):
    lat = models.FloatField(default=0)
    longt = models.FloatField(default=0)
    alt = models.FloatField(default=0)
    battery = models.CharField(max_length=100)
    mode = models.CharField(max_length=15)
    arm = models.CharField(max_length=10)
    def __str__(self):
        return self.mode