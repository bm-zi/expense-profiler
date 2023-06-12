from django.db import models

# Create your models here.
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User


class Income(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    source = models.CharField(max_length=255)

    # show category in queryset
    def __str__(self):
        return self.source

    class Meta:
        verbose_name_plural = "Income"
        ordering = ['-date']


class Source(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
