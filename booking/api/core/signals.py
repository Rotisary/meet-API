from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from booking.models import Meet, Appointment
from booking.api.core.tasks import send_booking_confirmation_email, send_scheduled_appointment_mail

import random, string


@receiver(pre_save, sender=Meet)
def generate_token(sender, instance, **kwargs):
    if instance.pk is None:
        instance.ID = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))


@receiver(post_save, sender=Meet)
def send_email(sender, instance, created, **kwargs):
    if created:
        patient_email = instance.patient.email
        doctor_email = instance.doctor.user.email
        meet_id = instance.ID
        
        send_booking_confirmation_email.delay(meet_id, patient_email, doctor_email)


@receiver(post_save, sender=Appointment)
def send_appointment_email(sender, instance, created, **kwargs):
    if created:
        patient_email = instance.patient.email
        send_scheduled_appointment_mail.delay(patient_email)