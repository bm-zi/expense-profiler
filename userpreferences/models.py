from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserPreference(models.Model):
    try:
        user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    except models.DoesNotExist:
        user = None
 
    currency = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.user:
            return str(self.user)+"preferences"
