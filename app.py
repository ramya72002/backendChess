from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, db
from flask_cors import CORS
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import json, time
from geopy.geocoders import Nominatim

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

app = Flask(__name__)
CORS(app)

# Load Firebase credentials from the JSON file
with open('credential.json') as f:
    firebase_cred = json.load(f)

cred = credentials.Certificate(firebase_cred)

firebase_admin.initialize_app(cred,{'databaseURL':'https://skincareapp-e9f8e-default-rtdb.firebaseio.com/'})

ref=db.reference('/')

translator = Translator()

users = []
preferred_language=""
def time_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
@app.route('/create',methods=['POST'])
def create():
    data=request.json
    if data:
        new_ref=ref.push(data)
        return jsonify({'message':'dta created','key':new_ref.key}),201
    else:
        return "error"

@app.route('/time')
def serve_time():
    return jsonify({"time": time_now()})

@app.route('/scc')
def serve_scc():
    with open('./data/scc.json', 'r', encoding='utf-8') as json_file:
        scc = json.load(json_file)  
    print({'tips': scc})
    return jsonify({'tips': scc})

@app.route('/bcc')
def serve_bcc():
    with open('./data/bcc.json', 'r', encoding='utf-8') as json_file:
        bcc = json.load(json_file)  
    print({'tips': bcc})
    return jsonify({'tips': bcc})

@app.route('/mem')
def serve_mem():
    with open('./data/melanoma.json', 'r', encoding='utf-8') as json_file:
        mem = json.load(json_file)  
    print({'tips': mem})
    return jsonify({'tips': mem})

@app.route('/sunsafety')
def serve_sunsafety():
    with open('./data/sunsafety.json', 'r', encoding='utf-8') as json_file:
        sunsafety = json.load(json_file)  
    print({'tips': sunsafety})
    return jsonify({'tips': sunsafety})

@app.route('/traditionalc')
def serve_traditionalc():
    with open('./data/traditionalclothing.json', 'r', encoding='utf-8') as json_file:
        traditionalc = json.load(json_file)  
    print({'tips': traditionalc})
    return jsonify({'tips': traditionalc})

@app.route('/uvindexdata')
def serve_uvindex():
    with open('./data/uvindex.json', 'r', encoding='utf-8') as json_file:
        uvindex = json.load(json_file)  
    print({'tips': uvindex})
    return jsonify({'tips': uvindex}) 
 

@app.route('/additional')
def serve_additional():
    with open('./data/additional.json', 'r', encoding='utf-8') as json_file:
        additional = json.load(json_file)  
    print({'tips': additional})
    return jsonify({'tips': additional})

@app.route('/Infectious')
def serve_Infectious():
    with open('./data/infectious.json', 'r', encoding='utf-8') as json_file:
        Infectious = json.load(json_file)  
    print({'tips': Infectious})
    return jsonify({'tips': Infectious})

@app.route('/inflaauto')
def serve_inflaauto():
    with open('./data/inflaauto.json', 'r', encoding='utf-8') as json_file:
        inflaauto = json.load(json_file)  
    print({'tips': inflaauto})
    return jsonify({'tips': inflaauto})

@app.route('/hair')
def serve_hair():
    with open('./data/hair.json', 'r', encoding='utf-8') as json_file:
        hair = json.load(json_file)  
    print({'tips': hair})
    return jsonify({'tips': hair})


@app.route('/pigmentary')
def serve_pigmentary():
    with open('./data/pigmentary.json', 'r', encoding='utf-8') as json_file:
        pigmentary = json.load(json_file)  
    print({'tips': pigmentary})
    return jsonify({'tips': pigmentary})

@app.route('/envdisorder')
def serve_envdisorder():
    with open('./data/envdisorder.json', 'r', encoding='utf-8') as json_file:
        envdisorder = json.load(json_file)  
    print({'tips': envdisorder})
    return jsonify({'tips': envdisorder})

def translate_words(sentences, dest_language):
    translated_sentences = []
    for sentence in sentences:
        translated_sentence = translator.translate(sentence, dest=dest_language).text
        translated_sentences.append(translated_sentence)
    print(translated_sentences)
    return translated_sentences

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    content = data.get('content')
    target_language = data.get('language')

    if not content or not target_language:
        return jsonify({'error': 'Content and language are required'}), 400

    try:
        translated_content = translate_words(content, target_language)
        return jsonify({'translated_text': translated_content})
    except ValueError as ve:
        return jsonify({'error': 'Invalid input', 'details': str(ve)}), 400
    except RuntimeError as re:
        return jsonify({'error': 'Translation error', 'details': str(re)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    user_data = request.get_json()
    if user_data:
        email = user_data.get('email')
        contact_number = user_data.get('contactNumber')
        
        # Check if user already exists
        users = ref.get()
        if users:
            for user_id, user in users.items():
                if isinstance(user, dict):
                    if user.get('email') == email and user.get('contactNumber') == contact_number:
                        return jsonify({'error': 'User already exists. Please login.'}), 400
        
        # Add new user data
        ref.push(user_data)
        return jsonify({'success': True}), 201
    else:
        return jsonify({'error': 'Invalid data format.'}), 400
@app.route('/login', methods=['POST'])
def login():
    login_data = request.get_json()
    email = login_data.get('email')
    contact_number = login_data.get('contactNumber')
    preferred_language = login_data.get('preferredLanguage')
    
    if not email or not contact_number:
        return jsonify({'error': 'Email and contact number are required'}), 400
    
    # Retrieve all users from the database
    users = ref.get()
    name=""
    if users:
        for user_id, user in users.items():
            if isinstance(user, dict):
                if user.get('email') == email and user.get('contactNumber') == contact_number:
                    name=user.get('name')
                    print(name)
                    return jsonify({'success': True, 'message': 'Login successful', 'preferredLanguage': preferred_language,'name':name}), 200
    return jsonify({'message': 'Email and Mobile Number is registered'}), 200


@app.route('/weather', methods=['POST'])
def get_weather():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    state = data.get('state')
    city = data.get('city')

    if not state or not city:
        return jsonify({'error': 'State and city are required'}), 400
    
    url = f'https://www.weatheronline.in/{state}/{city}.htm'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='gr1')
        if tables:
            table_data = extract_table_data(tables[0])
            return jsonify(table_data)
        else:
            return jsonify({'error': 'No table found with class "gr1"'})
    else:
        return jsonify({'error': 'Failed to fetch weather data'})

def extract_table_data(table):
    table_data = []
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all(['td', 'th']):
            row_data.append(cell.text.strip())
        table_data.append(row_data)
    return table_data


@app.route('/uvindex', methods=['POST'])
def get_uvindex():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    state = data.get('state')
    city = data.get('city')

    if not state or not city:
        return jsonify({'error': 'State and city are required'}), 400
    
    url = f'https://www.weatheronline.in/{state}/{city}/UVindex.htm'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='gr1')
        if tables:
            table_data = extract_table_data(tables[0])
            return jsonify(table_data)
        else:
            return jsonify({'error': 'No table found with class "gr1"'})
    else:
        return jsonify({'error': 'Failed to fetch uvindex data'})
    
@app.route('/wind', methods=['POST'])
def get_wind():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    state = data.get('state')
    city = data.get('city')

    if not state or not city:
        return jsonify({'error': 'State and city are required'}), 400
    
    url = f'https://www.weatheronline.in/{state}/{city}/Wind.htm'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table', class_='gr1')
        if tables:
            table_data = extract_table_data(tables[0])
            return jsonify(table_data)
        else:
            return jsonify({'error': 'No table found with class "gr1"'})
    else:
        return jsonify({'error': 'Failed to fetch wind data'})
    
def extract_city_names(t):
    city_names = []
    
    if t:
        city_links = t.find_all('a')
        
        for link in city_links:
            city_names.append(link.text.strip())
        
    return city_names
@app.route('/cities', methods=['POST'])
def get_cities():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    state = data.get('state')

    if not state:
        return jsonify({'error': 'State is required'}), 400
    
    url = f'https://www.weatheronline.in/{state}.htm'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        t = soup.find_all(class_="scroll_c1_r")
        city_names = []
        
        for element in t:
            city_links = element.find_all('a')
            for link in city_links:
                city_names.append(link.text.strip())
        
        return jsonify({'cities': city_names})
    else:
        return jsonify({'error': 'Failed to retrieve data from the server'}), 500
    
@app.route('/Doctordetails1', methods=['POST'])
def get_docdetails1():
    data = request.get_json()
    
    print(data)
    city = data.get('city')
    address=city
    geolocator = Nominatim(user_agent="Your_Name")
    location = geolocator.geocode(address)
    payload={"query": "", "page": 0, "getRankingInfo": True, "aroundRadius": 1000000, "aroundLatLng": f"{location.latitude},{location.longitude}"}
    print(payload)
    headers = {"Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": str(len(json.dumps(payload))),
        "Host": "55wtpyuy7q-dsn.algolia.net",
        "Origin": "https://find-a-derm.aad.org",
        "Referer": "https://find-a-derm.aad.org/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Content-Type": "application/json; charset=UTF-8",
        "Sec-Ch-UA": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "Sec-Ch-UA-Mobile": "?0",
        "Sec-Ch-UA-Platform": '"Windows"',
        "X-Algolia-API-Key": "41da89e44195a72b2d9d109eeee8db8f",
        "X-Algolia-Application-Id": "55WTPYUY7Q"}
    url = 'https://55wtpyuy7q-dsn.algolia.net/1/indexes/production/query'
    try:
        # Making the POST request with the payload
        response = requests.post(url, json=payload,headers=headers)
      

        # Checking if the request was successful
        if response.ok:
            # Retrieving the response data
            data = response.json()
            # Do something with the data, like returning it
            results = [
                    {
                        'name': hit['name'],
                        'phone': hit['locations'][0]['phone'],
                        'address': (
                                    hit['locations'][0]['address1'] + 
                                    hit['locations'][0]['address2'] + 
                                    hit['locations'][0]['address3']
                                )  ,
                        'city': hit['locations'][0]['city']
                       }
                    for hit in data['hits']
                ]

                # Returning the filtered results
            return jsonify({'true': results})
        else:
            # If the request was not successful, return an error message
            return "Failed to fetch doctor details", 500
    except Exception as e:
        # If an exception occurred during the request, return an error message
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
