from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='patient')
    email = models.EmailField(unique=True)


# class Doctor(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     specialty = models.CharField(max_length=100)

#     def __str__(self):
#         return self.user.username

# class DoctorAvailability(models.Model):
#     DAY_CHOICES = [
#         ("MON", "Monday"),
#         ("TUE", "Tuesday"),
#         ("WED", "Wednesday"),
#         ("THU", "Thursday"),
#         ("FRI", "Friday"),
#         ("SAT", "Saturday"),
#         ("SUN", "Sunday"),
#     ]
#     doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
#     day = models.CharField(max_length=3, choices=DAY_CHOICES)
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.doctor} - {self.day}"

