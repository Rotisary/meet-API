from django.db import models
from users.models import Profile
from django.conf import settings


class Symptom(models.Model):
    ID = models.IntegerField(unique=True, null=False, blank=False)
    Name = models.CharField(max_length=225, null=False, blank=False)


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
                                related_name='complaints', 
                                on_delete=models.CASCADE)
    symptoms = models.ManyToManyField(Symptom, related_name='complaints', blank=True)
    sex = models.CharField(choices=SEX_CHOICES, blank=False, null=False)
    year_of_birth = models.IntegerField(null=False, blank=False)
    age_group = models.CharField(choices=AGE_GROUP_CHOICES, default=PRETEEN, blank=False, null=False)
    treated_by = models.ForeignKey(Profile, 
                                   related_name='illness_treated', 
                                   blank=True, 
                                   null=True, 
                                   on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at', null=True)

    objects = models.Manager()
    

    def __str__(self):
        return f"complaint detail {self.id}"
    

class MeetManager(models.Manager):

    def get_active_meets(self):
        return super().get_queryset().filter(has_ended=False)
    

    def get_ended_meets(self):
        return super().get_queryset().filter(has_ended=True)
    

    def get_confirmed_meets(self):
        return super().get_queryset().filter(is_confirmed=True)


class Meet(models.Model):
    ID = models.CharField(max_length=6, blank=True, null=True, unique=True)
    doctor = models.ForeignKey(Profile, related_name='meets_booked_for', on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='meets_booked', on_delete=models.DO_NOTHING)
    complaint = models.OneToOneField(Complaint, related_name='meet_in', on_delete=models.DO_NOTHING)
    has_ended = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    objects = models.Manager()
    filtered_objects = MeetManager()


    def __str__(self):
        return f"{self.ID}"



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
