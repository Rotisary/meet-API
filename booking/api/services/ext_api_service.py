import os, requests, hmac, hashlib, base64
from dotenv import load_dotenv

load_dotenv()


def get_token(secret_key, requested_uri):
    bytes_secret_key = secret_key.encode('utf-8')
    bytes_requested_uri = requested_uri.encode('utf-8')
    hmac_md5 = hmac.new(bytes_secret_key, bytes_requested_uri, hashlib.md5)
    hashed_credentials = base64.b64encode(hmac_md5.digest()).decode('utf-8')
    api_key = os.getenv('APIMEDIC_API_KEY')

    headers = {'Authorization': f'Bearer {api_key}:{hashed_credentials}'}
    response = requests.post(requested_uri, headers=headers)
    if response.status_code != 200:
        return f"{response.status_code} {response.text}"
    else:
        return response.json()['Token']
    

def get_api_data(token, symptom, sex, year_of_birth):
    url = 'https://healthservice.priaid.ch/diagnosis'
    query_name = {
        'token': token,
        'language': 'en-gb',
        'symptoms': str([int(symptom)]),
        'gender': sex,
        'year_of_birth': year_of_birth      
    }

    response = requests.get(url, params=query_name)
    if response.status_code != 200:
        raise ValueError(response.text)
    else:
        issue_response = response.json()
        
    issues = []
    specialisations_list = []
    for data in issue_response:
        issue = data['Issue']['ProfName']
        issues.append(issue)
        specialisations = data['Specialisation']
        for specialisation in specialisations:
            specialisation_item = specialisation['Name']
            specialisations_list.append(specialisation_item)
    return specialisations_list, issues

# secret_key = os.getenv('APIMEDIC_SECRET_KEY')
# requested_uri = "https://authservice.priaid.ch/login"
# token = get_token(secret_key, requested_uri)

# print(get_api_data(token, [233], 'male', 2000))