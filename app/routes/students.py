from flask import Blueprint, request, jsonify
from app.database import users_collection

students_bp = Blueprint('students', __name__)

@students_bp.route('/studentList', methods=['GET'])
def get_studentList():
    try:
        documents = list(users_collection.find({}, {'_id': 0}))
        if documents:
            return jsonify(documents), 200
        else:
            return jsonify({"error": "No records found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@students_bp.route('/del-student', methods=['DELETE'])
def delete_student():
    try:
        email = request.json.get('email')
        if not email:
            return jsonify({"error": "Email is required"}), 400

        result = users_collection.delete_one({"email": email})
        if result.deleted_count > 0:
            return jsonify({"message": "Student record deleted successfully"}), 200
        else:
            return jsonify({"error": "Student record not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
