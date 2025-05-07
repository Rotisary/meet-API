from celery import shared_task
from rest_project.settings import EMAIL_HOST_USER
from django.core.mail import send_mail


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