from datetime import datetime
import random
from django.conf import settings
from django.utils.timezone import now,timedelta
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail,EmailMessage
from .models import Employee,OTP,Leave,PerformanceAnalysis
from .decorators import hr_or_admin_required

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

@login_required(login_url='/users/login')
def user_logout(request):
    logout(request)
    return redirect('/')

def about(request):
    if request.user.is_authenticated:
        employee = Employee.objects.filter(user = request.user).first()
        return render(request, 'about.html',{'employee': employee})
    return render(request,'about.html',{})

def features(request):
    if request.user.is_authenticated:
        employee = Employee.objects.filter(user = request.user).first()
        return render(request, 'features.html',{'employee': employee})
    return render(request,'features.html',{})

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if name and email and subject and message:
            email_message = EmailMessage(
                subject=subject,
                body=f"Message from {name} ({email}):\n\n{message}",
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.EMAIL_HOST_USER],
                headers={'Reply-To': email},  
            )
            email_message.send(fail_silently=False)
            messages.info(request,"Your Query has been sent !")
            return redirect('/contact')
        else:
            messages.info(request,"Please fill out all the details !")
    if request.user.is_authenticated:
        employee = Employee.objects.filter(user = request.user).first()
        return render(request, 'contact.html',{'employee': employee})
    return render(request,'contact.html',{})


def home(request):
    if request.user.is_authenticated:
        employee = Employee.objects.filter(user = request.user).first()
        return render(request, 'users/home.html',{'employee': employee})
    else:
        return render(request, 'users/home.html')

@login_required(login_url='/users/login')
@hr_or_admin_required
def employees(request):
    employee = Employee.objects.filter(user = request.user).first()
    if employee.designation == 'A':
        employees = Employee.objects.filter(Q(designation__in=['H', 'E']) | Q(user=request.user)).exclude(user = request.user)
    else:
        employees = Employee.objects.filter(designation='E')
    return render(request,'employees/employees.html',{ 'employees' : employees,'employee':employee })

@login_required(login_url='/users/login')
def employee(request,id):
    user = User.objects.filter(id = id).first()
    employee = Employee.objects.filter(user = user).first()
    performance = PerformanceAnalysis.objects.filter(employee=employee).order_by('review_period_start')
    labels = [f"{record.review_period_start.strftime('%b %Y')} - {record.review_period_end.strftime('%b %Y')}" for record in performance]
    ratings = [float(record.rating or 0) for record in performance]
    return render(request,'employees/employee.html',{ 'employee':employee,'labels':labels, 'ratings':ratings })

@login_required(login_url='/users/login')
def update_profile(request,id):
    user = User.objects.filter(id = id).first()
    employee = Employee.objects.filter(user = user).first()
    if request.method == "POST":
        if request.FILES.get('image') == None:
            pass
        else:
            employee.image = request.FILES.get('image')
        employee.job_title = request.POST.get('job_title')
        employee.gender = request.POST.get('gender')
        employee.years_of_working = request.POST.get('years_of_working')
        employee.contact = request.POST.get('contact')
        employee.department = request.POST.get('department')
        employee.save()
        return redirect(f'/employees/{user.id}')
    else:
        return render(request,'employees/profileupdate.html',{'employee':employee})

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
                employee = Employee.objects.get(user = user)
                if employee.designation == 'E':
                    return redirect(f"/employees/{user.id}")
                else:
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

@login_required(login_url='/users/login')
def apply_leave(request):
    if request.method == "POST":
        employee = Employee.objects.get(user=request.user)
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        try:
            leave = Leave(
                employee=employee,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )
            leave.save()
            messages.info(request, "Leave applied successfully.")
        except ValueError as e:
            messages.info(request, str(e))
        return redirect(f"/employees/{request.user.id}")
    return render(request,'employees/apply_leave.html',{})