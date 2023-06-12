from django.shortcuts import redirect, render
from django.views import View
import json
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
import smtplib
import os
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.urls import reverse, reverse_lazy
from .utils import token_generator
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from dotenv import load_dotenv

from .forms import UserDataForm, MyPasswordChangeForm
from django.views.generic.base import TemplateView
from django.contrib.auth import update_session_auth_hash

# Create your views here.

load_dotenv()

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumberic characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'The username already in use. Choose another username'}, status=409)
        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'The email already in use'}, status=409)
        return JsonResponse({'email_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'auth/register.html')

    def post(self, request):

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(
                        request, 'Password must be at least 6 characters long')
                    return render(request, 'auth/register.html', context)
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                uid64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={
                               'uid64': uid64, 'token': token_generator.make_token(user)})
                activate_url = f"http://{domain}{link}"
                send_activation_email(user.username, email, activate_url)

                messages.success(
                    request, 'Your account has been created!')
                return render(request, 'auth/register.html')
        return render(request, 'auth/register.html')


def send_activation_email(username, email, url):
    MyEmail = os.environ['EMAIL_HOST_USER']
    MyPassword = os.environ['EMAIL_HOST_PASSWORD']
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(MyEmail, MyPassword)
    email_subject = "Activate your account"

    email_body = f"Hi {username},\n\n Please use this link to activate your account. \n {url}"
    msg = f"Subject: {email_subject}\n\n{email_body}"
    # from MyEmail to email
    server.sendmail(MyEmail, email, msg)
    server.close()
    print('Email has been sent')


class VerificationView(View):
    def get(self, request, uid64, token):

        try:
            id = force_text(urlsafe_base64_decode(uid64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated!')
            print('account activated!')
            return redirect('login')
        except Exception as ex:
            print('something went wrong....')
            pass
        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' +
                                     user.username+'! You are now logged in.')
                    return redirect('/')
                messages.error(
                    request, 'Account is not active. Please check your email.')
                return render(request, 'auth/login.html')
            messages.error(
                request, 'Invalid credentials.')
            return render(request, 'auth/login.html')
        messages.error(
            request, 'Please fill in all fields.')
        return render(request, 'auth/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')

# request email to reset password


class PasswordResetEmailView(View):
    def get(self, request):
        return render(request, 'auth/reset-password.html')

    def post(self, request):

        context = {
            'values': request.POST
        }
        email = request.POST['email']

        if not validate_email(email):
            messages.error(request, 'Please submit a valid email')
            return render(request, 'auth/reset-password.html', context)

        users = User.objects.filter(email=email)
        if users.exists():
            user = users[0]
            uid64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            token = PasswordResetTokenGenerator().make_token(user)
            link = reverse('set-new-password', kwargs={
                'uid64': uid64, 'token': token})
            reset_url = f"http://{domain}{link}"

            send_password_reset_email(user.username, email, reset_url)
            messages.success(request, 'We have sent an email')
            return render(request, 'auth/reset-password.html', context)
        messages.error(request, 'This email does not exist')
        return render(request, 'auth/reset-password.html', context)


def send_password_reset_email(username, email, url):
    MyEmail = os.environ['EMAIL_HOST_USER']
    MyPassword = os.environ['EMAIL_HOST_PASSWORD']
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(MyEmail, MyPassword)
    email_subject = "Reset your password"

    email_body = f"Hi {username},\n\n Please use this link to reset your password. \n {url}"
    msg = f"Subject: {email_subject}\n\n{email_body}"
    # from MyEmail to email
    server.sendmail(MyEmail, email, msg)
    server.close()
    print('Email has been sent')


class NewPasswordView(View):
    def get(self, request, uid64, token):
        context = {
            'uid64': uid64,
            'token': token
        }
        return render(request, 'auth/set-new-password.html', context)

    def post(self, request, uid64, token):
        context = {
            'uid64': uid64,
            'token': token
        }
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'auth/set-new-password.html', context)
        if len(password) < 6:
            messages.error(
                request, 'Password must be at least 6 characters long')
            return render(request, 'auth/set-new-password.html', context)
        user_id = force_text(urlsafe_base64_decode(uid64))
        user = User.objects.get(pk=user_id)
        user.password = password
        user.save()
        messages.success(request, 'Password has been saved')
        return redirect('login')



class AccountUpdateView(TemplateView):
    """
    Update user data and password change
    """
    template_name = 'auth/profile_settings.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_data_form'] = UserDataForm(instance=user)
        context['password_change_form'] = MyPasswordChangeForm(user=self.request.user)

        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_data_form = UserDataForm(instance=user, data=request.POST)
        password_change_form = MyPasswordChangeForm(user=user, data=request.POST)

        if 'save_data' in request.POST:
            if user_data_form.is_bound and user_data_form.is_valid():
                user_data_form.save()
                update_session_auth_hash(request, request.user)
                messages.add_message(request, messages.SUCCESS, "User data updated")
                return redirect('/')
            else:
                messages.error(request, user_data_form.errors)


        elif 'save_password' in request.POST:
            if password_change_form.is_bound and password_change_form.is_valid():
                password_change_form.save()
                update_session_auth_hash(request, user)
                messages.add_message(request, messages.SUCCESS, "password changed")
            else:
                messages.error(request, password_change_form.errors)
        

        return HttpResponseRedirect(reverse('dashboard'))
