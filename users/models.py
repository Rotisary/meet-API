from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.template.defaultfilters import slugify


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
    API_USER = 'API'
    CATEGORY_CHOICE = [
        (DOCTOR, 'doctor'),
        (PATIENT, 'patient'),
        (API_USER, 'api user')
    ]
    email = models.EmailField(max_length=251, verbose_name='email', unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_api_user = models.BooleanField(default=False)
    category = models.TextField(choices=CATEGORY_CHOICE, max_length=20)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=11, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'category', 'first_name', 'last_name']

    objects = UserManager()


    def __str__(self):
        return f"{self.username}"
    

    def has_perm(self, perm, obj=None):
        return self.is_admin
    

    def has_module_perms(self, app_label):
        return True
    

class APIUser(User):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.category = 'API'
        self.is_api_user = True
        return super().save(*args, **kwargs)


class Profile(models.Model):
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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100,blank=False, null=False)
    patient_type = models.CharField(choices=AGE_GROUP_CHOICES, null=False, blank=False)
    meets = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='meets_in', blank=True)
    rating = models.FloatField(default=0)
    slug = models.SlugField(max_length=50, blank=False, null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='created_at')


    def __str__(self):
        return f"{self.user.username}'s profile"
    

    def number_of_meet(self):
        return self.meets.count()
    

    def save(self, *args, **kwargs):
        first_name = self.user.first_name
        last_name = self.user.last_name
        id = self.id
        self.slug = slugify(f"{first_name} {last_name} {id}")
        return super(Profile, self).save(*args, **kwargs)


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
    

@receiver(post_save, sender=APIUser)
def create_api_auth_token(sender, instance, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=APIUser)
def create_api_profile(sender, instance, created=False, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=APIUser)
def save_api_profile(sender, instance,  **kwargs):
    instance.profile.save()
