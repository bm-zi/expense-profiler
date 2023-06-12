from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.timezone import now
from .models import Item
 
class ImageForm(forms.Form):
    receipt_image = forms.ImageField()


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AddReceiptToExpenseForm(forms.ModelForm):
    """handles updating the recipt data saved in Item table"""
    class Meta:
        model = Item
        fields = ['shopping', 'item', 'price']