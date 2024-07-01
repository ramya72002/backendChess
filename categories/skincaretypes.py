from flask import jsonify
import json

def serve_scc():
    with open('./data/scc.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    scc = data.get("en", [])
    return jsonify({'tips': scc})

def serve_bcc():
    with open('./data/bcc.json', 'r', encoding='utf-8') as json_file:
        bcc = json.load(json_file)
    print({'tips': bcc})
    return jsonify({'tips': bcc})

def serve_mem():
    with open('./data/melanoma.json', 'r', encoding='utf-8') as json_file:
        mem = json.load(json_file)
    print({'tips': mem})
    return jsonify({'tips': mem})
