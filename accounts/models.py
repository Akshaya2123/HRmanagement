from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db import models
from datetime import timedelta

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
    
class Leave(models.Model):
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)

    def total_leave_days(self):
        return (self.end_date - self.start_date).days + 1

    def save(self, *args, **kwargs):
        leave_days = self.total_leave_days()
        if leave_days <= 0:
            raise ValueError("End date must be after or equal to the start date.")
        current_month_start = self.start_date.replace(day=1)
        next_month_start = (current_month_start + timedelta(days=31)).replace(day=1)
        existing_leaves = Leave.objects.filter(employee=self.employee,start_date__gte=current_month_start,start_date__lt=next_month_start)
        total_days = sum(leave.total_leave_days() for leave in existing_leaves)
        if total_days + leave_days > 3:
            raise ValueError("An employee can't take more than 3 days leave in a month.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.employee.user.username

class PerformanceAnalysis(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    review_period_start = models.DateField() 
    review_period_end = models.DateField() 
    goals_set = models.TextField(blank=True, null=True)    
    goals_achieved = models.TextField(blank=True, null=True) 
    manager_feedback = models.TextField(blank=True, null=True) 
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True) 

    def review_duration(self):
        return (self.review_period_end - self.review_period_start).days
    
    def get_goals_set(self):
        return self.goals_set.split(',')
    
    def get_goals_achieved(self):
        return self.goals_achieved.split(',')

    def __str__(self):
        return f"{self.employee.user.username} - {self.review_period_start} to {self.review_period_end}"
    
    def save(self, *args, **kwargs):
        total_duration = self.review_duration()
        if total_duration < 0:
            raise ValueError("End date must be after or equal to the start date.")
        start = self.review_period_start.replace(day=1)
        end = self.review_period_end.replace(day=1)
        existing_record = PerformanceAnalysis.objects.filter(
            employee=self.employee,
            review_period_start=start,
            review_period_end=end
        ).first()

        if existing_record:
            existing_record.goals_set += ','+self.goals_set
            existing_record.goals_achieved += ','+self.goals_achieved
            existing_record.manager_feedback = self.manager_feedback
            existing_record.rating += self.rating
            existing_record.save()
        else:
            self.review_period_start = start
            self.review_period_end = end
            super().save(*args, **kwargs)