import random
from django.conf import settings
from django.utils.timezone import now,timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Employee,OTP

User = get_user_model()

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        designation = request.POST.get('designation')
        if password1 != password2:
            messages.info(request,"Passwords don't match !")
            return redirect('register')
        elif User.objects.filter(email = email).exists():
            messages.info(request, "Email already taken !")
            return redirect('register')
        elif User.objects.filter(username = username).exists():
            messages.info(request, "Username already taken !")
            return redirect('register')
        else:
            user = User.objects.create_user(username = username,email = email, password = password1)
            user.save()
            Employee.objects.create(user = user,designation=designation)
            return redirect('login')
    else:
        return render(request, 'users/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            otp = generate_otp(user)
            send_otp(user,otp)
            request.session['user_id'] = user.id
            return redirect('/verify_otp')
        else:
            messages.error(request, "Invalid credentials !")
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

def generate_otp(user):
    OTP.objects.filter(user=user).delete()
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    OTP.objects.create(user=user,otp=otp,expires_at=now() + timedelta(minutes=10))
    return otp

def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request,"Invalid User !")
            return redirect('/users/login')
        else:
            user = User.objects.get(id = user_id)
            otp = OTP.objects.filter(user=user,otp=otp,expires_at__gt=now()).first()
            if otp:
                login(request,user)
                otp.delete()
                request.session.pop('user_id',None)
                return redirect('home')
            else:
                messages.error(request,"Invalid or Expired OTP !")
                return redirect('/verify_otp')
    else:
        return render(request,'users/verify_otp.html')
    
def request_new_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request,"Invalid User !")
        return redirect('/users/login')
    else:
        user = User.objects.get(id = user_id)
        otp = generate_otp(user)
        send_otp(user, otp)
        messages.success(request, 'A new OTP has been sent to your email.')
        return redirect('/verify_otp')

def send_otp(user, otp):
    subject = 'OTP Verification'
    message = f'Hello {user.username},\n\nYour OTP code is {otp}.\n\nIt will expire in 10 minutes.'
    recipient_list = [user.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)