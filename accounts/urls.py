from django.urls import path
from . import views

urlpatterns = [
    path('users/register/', views.register, name='register'),
    path('users/login/', views.user_login, name='login'),
    path('users/logout/', views.user_logout, name='logout'),
    path('', views.home, name='home'),
    path('employees/',views.employees,name='employees'),
    path('employees/<str:id>',views.employee,name='employee'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('features/',views.features,name='features'),
    path('update_profile/<str:id>',views.update_profile,name='update_profile'),
    path('verify_otp/',views.verify_otp,name='verify-otp'),
    path('request_new_otp/',views.request_new_otp,name='request_new_otp'),
    path('apply_leave/',views.apply_leave,name="apply_leave"),
    path('get_performance_data/<str:id>',views.performance_chart,name="get_performance_data"),
    path('get_attendance_data/<str:id>',views.attendance_chart,name="get_attendance_data"),
    ]