from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db import models

User = get_user_model()
    
class Employee(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    contact = models.CharField(max_length=15,blank=True)
    image = models.ImageField(upload_to='products',blank=True,null=True)
    job_title = models.CharField(max_length=50,blank=True)
    years_of_working = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=1,choices=[('M','Male'),('F','Female'),('O','Other')],blank=True)
    department = models.CharField(max_length=50,blank=True)
    hire_date = models.DateTimeField(auto_now_add=True)
    salary = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    designation = models.CharField(choices=[('E','Employee'),('H','HR Manager'),('A','Admin')],max_length=1)

    def __str__(self):
        return self.user.username
    
class OTP(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return now() < self.expires_at
