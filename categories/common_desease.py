from flask import jsonify
import json

def serve_additional():
    with open('./data/additional.json', 'r', encoding='utf-8') as json_file:
        additional = json.load(json_file)
    print({'tips': additional})
    return jsonify({'tips': additional})

def serve_infectious():
    with open('./data/infectious.json', 'r', encoding='utf-8') as json_file:
        infectious = json.load(json_file)
    print({'tips': infectious})
    return jsonify({'tips': infectious})

def serve_inflaauto():
    with open('./data/inflaauto.json', 'r', encoding='utf-8') as json_file:
        inflaauto = json.load(json_file)
    print({'tips': inflaauto})
    return jsonify({'tips': inflaauto})

def serve_hair():
    with open('./data/hair.json', 'r', encoding='utf-8') as json_file:
        hair = json.load(json_file)
    print({'tips': hair})
    return jsonify({'tips': hair})

def serve_pigmentary():
    with open('./data/pigmentary.json', 'r', encoding='utf-8') as json_file:
        pigmentary = json.load(json_file)
    print({'tips': pigmentary})
    return jsonify({'tips': pigmentary})

def serve_envdisorder():
    with open('./data/envdisorder.json', 'r', encoding='utf-8') as json_file:
        envdisorder = json.load(json_file)
    print({'tips': envdisorder})
    return jsonify({'tips': envdisorder})
