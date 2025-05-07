def split_symptoms(symptoms):
    splited_symptoms = symptoms.split('_')
    symptoms_list = []
    for item in splited_symptoms:
        symptoms_list.append(int(item))

    return symptoms_list


def add_complaint_symptoms(symptoms_list, Symptom, complaint, not_found):
    for symptom in symptoms_list:
        try:
            model_symptom = Symptom.objects.get(ID=symptom)
            complaint.symptoms.add(model_symptom)
        except Symptom.DoesNotExist:
            raise not_found(detail="sorry, couldn't process your symptom. Please use different keywords")