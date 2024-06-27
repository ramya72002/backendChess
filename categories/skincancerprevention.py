from flask import Flask, jsonify, request
from flask_cors import CORS
import json
app = Flask(__name__)
CORS(app)
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