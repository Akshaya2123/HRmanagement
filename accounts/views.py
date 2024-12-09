from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Employee

User = get_user_model()

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.info(request,"Passwords don't match.")
            return redirect('register')
        elif User.objects.filter(email = email).exists():
            messages.info(request, "Email already taken.")
            return redirect('register')
        else:
            user = User.objects.create_user(username = username,email = email, password = password1)
            user.save()
            Employee.objects.create(user = user)
            return redirect('login')
    else:
        return render(request, 'users/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('/users/login')
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def home(request):
    return render(request, 'users/home.html')

def employees(request):
     employees = Employee.objects.all()
     return render(request,'employees/employees.html',{ 'employees' : employees })
