from flask import Flask, jsonify, request
from flask_cors import CORS
import json
app = Flask(__name__)
CORS(app)
from geopy.geocoders import Nominatim
import requests
 
@app.route('/Doctordetails1', methods=['POST'])
def get_docdetails1():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    city = data.get('city')
    address = city
    
    # Geocoding the address to get latitude and longitude
    geolocator = Nominatim(user_agent="Your_Name")
    location = geolocator.geocode(address)
    
    if not location:
        return jsonify({'error': f'Geolocation failed for address: {address}'}), 400
    
    payload = {
        "query": "",
        "page": 0,
        "getRankingInfo": True,
        "aroundRadius": 1000000,
        "aroundLatLng": f"{location.latitude},{location.longitude}"
    }
    
    headers = {
        "Accept": "*/*",
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
        "X-Algolia-Application-Id": "55WTPYUY7Q"
    }
    
    url = 'https://55wtpyuy7q-dsn.algolia.net/1/indexes/production/query'
    
    try:
        print(url)
        # Making the POST request with the payload
        response = requests.post(url, json=payload, headers=headers)
      
        # Checking if the request was successful
        if response.ok:
            # Retrieving the response data
            data = response.json()
            # Processing the hits to extract necessary details
            results = [
                {
                    'name': hit['name'],
                    'phone': hit['locations'][0]['phone'],
                    'address': (
                        hit['locations'][0]['address1'] + 
                        hit['locations'][0]['address2'] + 
                        hit['locations'][0]['address3']
                    ),
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
