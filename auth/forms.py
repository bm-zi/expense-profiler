from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django import forms


class UserDataForm(forms.ModelForm):
    """
    Create a form to update user data
    """
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class MyPasswordChangeForm(PasswordChangeForm):
    """
    Create a form to update user password
    """
    class Meta:
        model = User
        fields = "__all__"
