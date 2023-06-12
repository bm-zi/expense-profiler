from django.db import models
from django.contrib.auth.models import User

from PIL import Image 
from .image_processing import  findDocumentContour, covert2Gray
from imutils.perspective import four_point_transform
import cv2
import numpy as np


class Shopping(models.Model):
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    place = models.CharField(max_length=50, blank=True, null=True)
    full_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    img_file = models.CharField(max_length=100, blank=True, null=True)


class Item(models.Model):
    shopping = models.ForeignKey(Shopping, on_delete=models.CASCADE)
    item = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)


class Receipt(models.Model):
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    img = models.ImageField(upload_to= "receiptImages/")
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-date"]
        
    def __str__(self):
        return "receiptPhoto"