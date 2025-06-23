import os
from dotenv import load_dotenv
from booking.api.services.ext_api_service import get_token, get_api_data

load_dotenv()


def get_func_arguments(complaint):
    symptom = complaint.symptom
    sex = complaint.sex
    year_of_birth = complaint.year_of_birth
    age_group = complaint.age_group
    return symptom, sex, year_of_birth, age_group


def filter_doctors(complaint, profile, serializer, request):
    # get apimedic authentication token
    secret_key = os.getenv('APIMEDIC_SECRET_KEY')
    requested_uri = "https://authservice.priaid.ch/login"
    token = get_token(secret_key, requested_uri)

    # get external api results
    symptom, sex, year_of_birth, age_group = get_func_arguments(complaint)
    specialisations_list, issues = get_api_data(token, symptom, sex, year_of_birth)

    # filter results and add relevant doctors to new list
    doctors = profile.objects.all()
    doctors_that_match = []
    for doctor in doctors:
        for specialisation_data in specialisations_list:
            if doctor.specialization == specialisation_data and doctor.patient_type == age_group:
                doctors_that_match.append(doctor)         

    data = { 'possible illness': issues }
    if not doctors_that_match:
        data['message'] = "sorry, we don't any have doctor that can treat your probable illness. Please try again later"
    else:
        doctors_that_match_clean = set(sorted(doctors_that_match, key=lambda doctor: -doctor.rating))

        # serialize data and remove unwanted fields
        doctor_data_serializer = serializer(doctors_that_match_clean, many=True, context={'request': request})
        for object in doctor_data_serializer.data:
            object.pop('meets_booked_for')
            object.pop('appointments_booked')
            object.pop('id')
            object.pop('slug')
            object.pop('reviews')

        data['doctor suggestions'] = doctor_data_serializer.data
    return data