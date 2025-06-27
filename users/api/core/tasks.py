from celery import shared_task
from rest_project.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from users.models import Profile


@shared_task
def send_otp_mail(email, otp):
    
    subject = 'password reset'
    message = f'''this is your password reset otp :{otp}. 
                Note: it is only valid for 5 minutes'''
    from_email = EMAIL_HOST_USER
    recipient_list = [email]
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print(f'error sending email. error: {e}')
        return False
    

@shared_task
def update_rating(profile_id):
    profile = Profile.objects.get(id=profile_id)
    profile_reviews = profile.reviews.all() 
    no_of_reviews = profile_reviews.count()
    sum_of_stars = 0
    for review in profile_reviews:
        sum_of_stars += review.stars
    try:
        profile.rating = round(sum_of_stars/no_of_reviews, 1)
    except ZeroDivisionError:
        profile.rating = 0
    profile.save()
    return True