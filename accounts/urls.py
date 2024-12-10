from django.urls import path
from . import views

urlpatterns = [
    path('users/register/', views.register, name='register'),
    path('users/login/', views.user_login, name='login'),
    path('users/logout/', views.user_logout, name='logout'),
    path('', views.home, name='home'),
    path('employees/',views.employees,name='employees'),
    path('verify_otp/',views.verify_otp,name='verify-otp'),
    path('request_new_otp/',views.request_new_otp,name='request_new_otp')]