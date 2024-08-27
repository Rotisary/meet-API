from django.db import models
from users.models import Profile
from django.conf import settings


class Illness(models.Model):
    EYE = 'EY'
    EAR = 'ER'
    NOSE = 'NS'
    SKIN = 'SK'
    DENTAL = 'DT'
    BONE = 'BN'
    MALARIA = 'ML'
    TYPHOID = 'TY'
    DIABETES = 'DB'
    URINARY_TRACT_INFECTION = 'UTI'
    SEX_ORGAN_ILLNESS = 'SOI' 
    BODY_PART_CHOICES = [
        (EYE, 'eye'),
        (EAR, 'ear'),
        (NOSE, 'nose'),
        (SKIN, 'skin'),
        (DENTAL, 'mouth&dental'),
        (BONE, 'bone')
    ]
    SPECIFIC_ILLNESS_CHOICES = [
        (MALARIA, 'malaria'),
        (TYPHOID, 'typhoid'),
        (DIABETES, 'diabetes'),
        (URINARY_TRACT_INFECTION, 'urinary tract infection'),
        (SEX_ORGAN_ILLNESS, 'sex organ illness'),
    ]
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                related_name='illness', 
                                on_delete=models.CASCADE)
    body_part = models.CharField(choices=BODY_PART_CHOICES, blank=True, null=True)
    specific_illness = models.CharField(choices=SPECIFIC_ILLNESS_CHOICES, blank=True, null=True)
    age = models.IntegerField(blank=False, null=False)
    treated_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                      related_name='illness_treated', 
                                      blank=True, 
                                      null=True, 
                                      on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at', null=True)

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
    



