from django.db import models


# Create your models her
class Locations(models.Model):
    destination = models.CharField(max_length=500)
    reference = models.CharField(max_length=500)
    free = models.BooleanField()
    lat = models.CharField(max_length=200, blank=True, null=True)
    lng = models.CharField(max_length=200, blank=True, null=True)
    place_id = models.CharField(max_length=200, blank=True, null=True)
    time = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.destination
