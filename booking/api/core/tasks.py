from celery import shared_task
from django.core.mail import send_mail, send_mass_mail
from rest_framework.reverse import reverse
from rest_project.settings import EMAIL_HOST_USER
from django.conf import settings


@shared_task
def send_booking_confirmation_email(meet_id, patient_email, doctor_email):
    subject = 'Booking Confirmation'
    from_email = EMAIL_HOST_USER
    patient_message = f'New meet has been booked successfully. Meet ID: {meet_id}'
    doctor_message = f'You have been booked for a new meet. Visit the site to confirm the meet. Meet ID: {meet_id}'
    
    mail_1 = (subject, patient_message, from_email, [patient_email])
    mail_2 = (subject, doctor_message, from_email, [doctor_email])

    try:
        send_mass_mail((mail_1, mail_2, ), fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    

@shared_task
def send_meet_end_email(meet_id, patient_email, doctor_email):
    subject = 'Meet Ended'
    from_email = EMAIL_HOST_USER
    patient_message = f'Your meet has ended. Meet ID: {meet_id}'
    doctor_message = f'Your meet has ended. Meet ID: {meet_id}'
    
    mail_1 = (subject, patient_message, from_email, [patient_email])
    mail_2 = (subject, doctor_message, from_email, [doctor_email])

    try:
        send_mass_mail((mail_1, mail_2,), fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    

@shared_task
def send_scheduled_appointment_mail(patient_email):
    subject = 'New Appointment'
    from_email = EMAIL_HOST_USER
    message = 'You have a new appointment scheduled'
    recipient_list = [patient_email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False