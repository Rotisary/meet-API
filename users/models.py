from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class UserManager(BaseUserManager):
    def create_user(self, email, username, category, first_name, last_name, password=None):
        if not email:
            raise ValueError("users must have an email address")
        if not username:
            raise ValueError("users must have a username")
        if not category:
            raise ValueError("users must choose a category")
        if not first_name:
            raise ValueError("users must enter a first_name")
        if not last_name:
            raise ValueError("users must enter a last_name")
        

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            category = category,
            first_name = first_name,
            last_name = last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
        

    def create_superuser(self, email, username, category, first_name, last_name, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            category = category,
            first_name = first_name,
            last_name = last_name,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    DOCTOR = 'DR'
    PATIENT = 'PT'
    CATEGORY_CHOICE = [
        (DOCTOR, 'doctor'),
        (PATIENT, 'patient'),
    ]
    email = models.EmailField(verbose_name='email', unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    category = models.TextField(choices=CATEGORY_CHOICE, max_length=20)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'category', 'first_name', 'last_name']

    objects = UserManager()


    def __str__(self):
        return f"{self.username}"
    

    def has_perm(self, perm, obj=None):
        return self.is_admin
    

    def has_module_perms(self, app_label):
        return True


class Profile(models.Model):
    OPTHAMOLOGIST = 'EY'
    OTOLARYNGOLOGIST = 'ENT'
    DERMATOLOGY = 'SK'
    DENTIST = 'DT'
    PHYSIOTHERAPIST = 'BN'
    PHYSICIAN = 'PN'
    UROLOGIST = 'UTI'
    GYNECOLOGIST = 'SOI'
    FIELD_CHOICES = [
        (OPTHAMOLOGIST, 'opthamologist'),
        (OTOLARYNGOLOGIST, 'otolaryngologist'),
        (DERMATOLOGY, 'dermatologist'),
        (DENTIST, 'dentist'),
        (PHYSIOTHERAPIST, 'physiotherapist'),
        (PHYSICIAN, 'physician'),
        (UROLOGIST, 'urologist'),
        (GYNECOLOGIST, 'gynecologist'),
    ] 
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    specialized_field = models.TextField(choices=FIELD_CHOICES, blank=False, null=False)
    doctor_type = models.TextField(null=False, blank=False)
    meet = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='meets', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')


    def __str__(self):
        return f"{self.user.username}'s profile"
    

    def number_of_meet(self):
        return self.meet.count()


class DoctorReview(models.Model):
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews_written', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Profile, related_name='reviews', on_delete=models.CASCADE)
    body = models.TextField(blank=False)
    stars = models.IntegerField(null=False)
    good = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')  


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created=False, **kwargs):
    if created:
        if instance.category == 'DR':
            Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance,  **kwargs):
        if instance.category == 'DR':
            instance.profile.save()
    

