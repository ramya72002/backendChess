from bson import ObjectId
from flask import Blueprint, request, jsonify
from app.database import admin_collection
import re

upcomming_bp = Blueprint('upcomingActivities', __name__)

@upcomming_bp.route('/add-upcomingActivities', methods=['POST'])
def add_upcomingActivities():
    data = request.json
    required_fields = ['title','date', 'time' ]
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"'{field}' is required"}), 400

    try:
        # Add the new upcomingActivities to the first document in the collection
        result = admin_collection.update_one(
            {},  # match the first document
            {'$push': {'upcoming_activities': data}}
        )
        if result.modified_count == 1:
            return jsonify({'message': 'upcomingActivities added successfully'}), 201
        else:
            return jsonify({'error': 'No document was updated'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@upcomming_bp.route('/del-upcomingActivitiess', methods=['DELETE'])
def delete_upcomingActivities():
    data = request.json

    # Validate data
    if not all(key in data for key in ('date', 'time','title')):
        return jsonify({"error": "Date and time must be provided to delete a upcomingActivities"}), 400

    try:
        # Remove the upcomingActivities from the upcomingActivitiess field
        result = admin_collection.update_one(
            {"upcoming_activities": {"$elemMatch": {"date": data['date'], "time": data['time'],"title":data["title"]}}},
            {"$pull": {"upcoming_activities": {"date": data['date'], "time": data['time'],"title":data["title"]}}}
        )

        if result.modified_count > 0:
            return jsonify({"message": "upcomingActivities deleted successfully"}), 200
        else:
            return jsonify({"error": "upcomingActivities not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
