from django.db import models
from users.models import Profile
from django.conf import settings
from django.db.models.manager import BaseManager


class Symptom(models.Model):
    ID = models.IntegerField(unique=True, null=False, blank=False)
    Name = models.CharField(null=False, blank=False)


    def __str__(self):
        return f"{self.Name}"


class Complaint(models.Model):
    PRETEEN = 'PT'
    TEENAGER = 'TN'
    ADULT = 'AD'
    OLD_ADULT = 'OAD'
    AGE_GROUP_CHOICES = [
        (PRETEEN, 'Preteen'),
        (TEENAGER, 'Teenager'),
        (ADULT, 'Adult'),
        (OLD_ADULT, 'Old Adult')
    ]
    MALE = 'male'
    FEMALE = 'female'
    SEX_CHOICES = [
        (MALE, 'male'),
        (FEMALE, 'female')
    ]
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                related_name='illness', 
                                on_delete=models.CASCADE)
    symptoms = models.ManyToManyField(Symptom, related_name='complaints', blank=True)
    sex = models.CharField(choices=SEX_CHOICES, blank=True, null=True)
    year_of_birth = models.IntegerField(null=True, blank=True)
    age_group = models.CharField(choices=AGE_GROUP_CHOICES, default=PRETEEN,blank=False, null=False)
    treated_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                      related_name='illness_treated', 
                                      blank=True, 
                                      null=True, 
                                      on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at', null=True)

    objects = models.Manager()
    

    def __str__(self):
        return f"illness detail {self.id}"


class Appointment(models.Model):
    owner = models.ForeignKey(Profile,
                              related_name='appointments_booked', 
                              null=False, 
                              on_delete=models.CASCADE)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL,   
                                related_name='appointments_in', 
                                null=False, 
                                on_delete=models.DO_NOTHING)
    date_of_appointment = models.DateField(null=False)
    time_of_appointment = models.TimeField(null=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')


    def __str__(self):
        return f"{self.owner.user.username}'s appointment, appointment {self.id}"
    



