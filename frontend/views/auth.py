# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib import messages
from frontend.forms import SignupForm, LoginForm

User = get_user_model()


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='users.backends.EmailOrPhoneBackend')
            messages.success(request, "Registration Successful!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email_or_phone = form.cleaned_data['email_or_phone']
            password = form.cleaned_data['password']

            user = authenticate(
                request, email_or_phone=email_or_phone, password=password
            )

            if user is not None:
                login(request, user)
                messages.success(request, "Login Successful!")
                return redirect('home')
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)  # This clears the session and logs out the user
    return redirect('/')  # redirect to homepage
