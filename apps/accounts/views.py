from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import uuid

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        email_or_username = request.POST.get('username') or request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=email_or_username, password=password)
        
        if user is not None:
            if user.is_locked:
                messages.error(request, 'Your account is locked due to too many failed login attempts. Please contact support.')
                return render(request, 'accounts/login.html')
                
            login(request, user)
            
            if remember_me:
                request.session.set_expiry(1209600) # 2 weeks
            else:
                request.session.set_expiry(0) # Browser close
                
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid credentials.')
            
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not email or not username or not password:
            messages.error(request, 'All fields (Username, Email, Password) are required.')
            return render(request, 'accounts/register.html', {'username': username, 'email': email})
            
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html', {'username': username, 'email': email})
            
        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return render(request, 'accounts/register.html', {'username': username, 'email': email})
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html', {'username': username, 'email': email})
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'accounts/register.html', {'username': username, 'email': email})
            
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_verified=False # Requires email verification
        )
        
        # In a full implementation, send verification email with token here.
        # send_mail(...)
        
        messages.success(request, 'Registration successful. Please log in.')
        return redirect('accounts:login')
        
    return render(request, 'accounts/register.html')

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('system_admin:dashboard')
        
    if request.method == 'POST':
        email_or_username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email_or_username, password=password)
        
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('system_admin:dashboard')
            else:
                messages.error(request, 'Access Denied: Administrator privileges required.')
        else:
            messages.error(request, 'Invalid credentials.')
            
    return render(request, 'accounts/admin_login.html')
