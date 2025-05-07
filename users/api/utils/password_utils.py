import random
from django.core.cache import cache
from rest_project.settings import EMAIL_HOST_USER
from users.api.core.tasks import send_otp_mail


def generate_otp(email):
    # generate otp
    otp = random.randint(100000, 999999)
    cache.set(f"{email}_otp", otp, timeout=300)

    # send otp to email
    send_otp_mail.delay(email, otp)
    return True