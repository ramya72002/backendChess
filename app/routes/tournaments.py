from flask import Blueprint, request, jsonify
from app.database import admin_collection
from bson import ObjectId
from pymongo import errors

tournaments_bp = Blueprint('tournaments', __name__)

@tournaments_bp.route('/tournaments', methods=['POST'])
def create_tournament():
    data = request.json
    required_fields = ['name', 'date', 'type', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"'{field}' is required"}), 400

    try:
        tournament = {
            'name': data['name'],
            'date': data['date'],
            'type': data['type'],
            'description': data['description']
        }
        result = admin_collection.insert_one(tournament)
        return jsonify({'message': 'Tournament created successfully', 'id': str(result.inserted_id)}), 201
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500

@tournaments_bp.route('/tournaments/<tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    try:
        tournament = admin_collection.find_one({'_id': ObjectId(tournament_id)})
        if not tournament:
            return jsonify({'error': 'Tournament not found'}), 404
        tournament['_id'] = str(tournament['_id'])
        return jsonify(tournament), 200
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500

@tournaments_bp.route('/tournaments', methods=['GET'])
def get_tournaments():
    try:
        tournaments = list(admin_collection.find())
        for tournament in tournaments:
            tournament['_id'] = str(tournament['_id'])
        return jsonify(tournaments), 200
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500

@tournaments_bp.route('/tournaments/<tournament_id>', methods=['PUT'])
def update_tournament(tournament_id):
    data = request.json
    update_fields = {}
    for field in ['name', 'date', 'type', 'description']:
        if field in data:
            update_fields[field] = data[field]

    try:
        result = admin_collection.update_one({'_id': ObjectId(tournament_id)}, {'$set': update_fields})
        if result.matched_count > 0:
            return jsonify({'message': 'Tournament updated successfully'}), 200
        else:
            return jsonify({'error': 'Tournament not found'}), 404
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500

@tournaments_bp.route('/tournaments/<tournament_id>', methods=['DELETE'])
def delete_tournament(tournament_id):
    try:
        result = admin_collection.delete_one({'_id': ObjectId(tournament_id)})
        if result.deleted_count > 0:
            return jsonify({'message': 'Tournament deleted successfully'}), 200
        else:
            return jsonify({'error': 'Tournament not found'}), 404
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500
