from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import requests,json
from bs4 import BeautifulSoup
from googletrans import Translator
from pymongo import MongoClient
from time_utils import serve_time
from categories.skincaretypes import serve_scc, serve_bcc, serve_mem
from categories.skincancerprevention import serve_sunsafety,serve_traditionalc,serve_uvindex
from categories.common_desease import serve_additional, serve_infectious, serve_inflaauto, serve_hair, serve_pigmentary, serve_envdisorder
from finddoctor.docdetails import get_docdetails1
from dotenv import load_dotenv
import os
 
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

app = Flask(__name__)
CORS(app)
load_dotenv()

# Get the MongoDB URI from the environment variable
mongo_uri = os.getenv('MONGO_URI')
# MongoDB setup
client = MongoClient(mongo_uri)
db = client.skincaredb
users_collection = db.user_details

translator = Translator()

@app.route('/')
def home():
    return "Hello, Flask on Vercel!"

def time_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@app.route('/create', methods=['POST'])
def create():
    data = request.json
    if data:
        result = users_collection.insert_one(data)
        return jsonify({'message': 'Data created', 'id': str(result.inserted_id)}), 201
    else:
        return "error", 400
    
@app.route('/signup', methods=['POST'])
def signup():
    user_data = request.get_json()
    if user_data:
        email = user_data.get('email')
        contact_number = user_data.get('contactNumber')
        
        # Check if user already exists
        existing_user = users_collection.find_one({'email': email, 'contactNumber': contact_number})
        if existing_user:
            return jsonify({'error': 'User already exists. Please login.'}), 400
        
        # Add new user data
        users_collection.insert_one(user_data)
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
    
    # Retrieve the user from the database
    user = users_collection.find_one({'email': email, 'contactNumber': contact_number})
    print(user)
    print(users_collection)
    print(db)
    
    if user:
        name = user.get('name')
        return jsonify({'success': True, 'message': 'Login successful', 'preferredLanguage': preferred_language, 'name': name}), 200
    return jsonify({'message': 'Email and Mobile Number is not registered'}), 400

# Register the /time route
app.add_url_rule('/time', 'serve_time', serve_time)
app.add_url_rule('/scc', 'serve_scc', serve_scc)
app.add_url_rule('/bcc', 'serve_bcc', serve_bcc)
app.add_url_rule('/mem', 'serve_mem', serve_mem)

app.add_url_rule('/sunsafety', 'serve_sunsafety', serve_sunsafety)
app.add_url_rule('/traditionalc', 'serve_traditionalc', serve_traditionalc)
app.add_url_rule('/uvindexdata', 'serve_uvindex', serve_uvindex)
 
app.add_url_rule('/additional', 'serve_additional', serve_additional)
app.add_url_rule('/infectious', 'serve_infectious', serve_infectious)
app.add_url_rule('/inflaauto', 'serve_inflaauto', serve_inflaauto)
app.add_url_rule('/hair', 'serve_hair', serve_hair)
app.add_url_rule('/pigmentary', 'serve_pigmentary', serve_pigmentary)
app.add_url_rule('/envdisorder', 'serve_envdisorder', serve_envdisorder)

app.route('/Doctordetails1', methods=['POST'])(get_docdetails1)

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
    print("------------",data)
    print(target_language)
    print(content)

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



@app.route('/scctranslate', methods=['POST'])
def translate_text_scct():
    data = request.get_json()
    target_language = data.get('language', 'en') 
    with open('./data/scc.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    scc = data.get(target_language, [])
    return jsonify({'tips': scc})


@app.route('/bcctranslate', methods=['POST'])
def translate_text_bcct():
    data = request.get_json()
    target_language = data.get('language', 'en') 
    with open('./data/bcc.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    bcc = data.get(target_language, [])
    return jsonify({'tips': bcc})

@app.route('/memtranslatet', methods=['POST'])
def translate_text_memt():
    data = request.get_json()
    target_language = data.get('language', 'en') 
    with open('./data/melanoma.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    mem = data.get(target_language, [])
    return jsonify({'tips': mem})



@app.route('/sunsafetyt', methods=['POST'])
def serve_sunsafetyt():
    data = request.get_json()
    target_language = data.get('language', 'en') 
    with open('./data/sunsafety.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    mem = data.get(target_language, [])
    return jsonify({'tips': mem})

@app.route('/traditionalct', methods=['POST'])
def serve_traditionalct():
    data = request.get_json()
    target_language = data.get('language', 'en') 
    with open('./data/traditionalclothing.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    mem = data.get(target_language, [])
    return jsonify({'tips': mem})

@app.route('/uvindexdatat', methods=['POST'])
def serve_uvindext():
    data = request.get_json()
    target_language = data.get('language', 'en') 
    with open('./data/uvindex.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    mem = data.get(target_language, [])
    return jsonify({'tips': mem})
    
@app.route('/additionalt', methods=['POST'])    
def serve_additionalt():
    data = request.get_json()
    target_language = data.get('language', 'en')
    with open('./data/additional.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    mem = data.get(target_language, [])
    return jsonify({'tips': mem})

@app.route('/infectioust', methods=['POST'])    
def serve_infectioust():
    data = request.get_json()
    target_language = data.get('language', 'en')
    print(data)
    with open('./data/infectious.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    mem = data.get(target_language, [])
    print(mem)
    return jsonify({'tips': mem})

@app.route('/inflaautot', methods=['POST'])    
def serve_inflaautot():
    data = request.get_json()
    target_language = data.get('language', 'en')
    print(data)
    with open('./data/inflaauto.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    mem = data.get(target_language, [])
    print(mem)
    return jsonify({'tips': mem})

@app.route('/hairt', methods=['POST'])    
def serve_hairt():
    data = request.get_json()
    target_language = data.get('language', 'en')
    with open('./data/hair.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    mem = data.get(target_language, [])
    return jsonify({'tips': mem})

@app.route('/pigmentaryt', methods=['POST'])    
def serve_pigmentaryt():
    data = request.get_json()
    target_language = data.get('language', 'en')
    with open('./data/Pigmentary.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    mem = data.get(target_language, [])
    return jsonify({'tips': mem})

@app.route('/envdisordert', methods=['POST'])    
def serve_envdisordert():
    data = request.get_json()
    target_language = data.get('language', 'en')
    print(data)
    with open('./data/envdisorder.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    mem = data.get(target_language, [])
    print(mem)
    return jsonify({'tips': mem})


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
    

if __name__ == '__main__':
    app.run()
