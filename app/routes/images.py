from flask import Blueprint, request, jsonify, send_file
from app.database import db, fs
from bson import ObjectId
from io import BytesIO
from pymongo import errors

images_bp = Blueprint('images', __name__)

@images_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'images' not in request.files or 'title' not in request.form:
        return jsonify({'error': 'No images or title part in the request'}), 400

    title = request.form['title']
    files = request.files.getlist('images')
    file_ids = []
    for file in files:
        try:
            file_id = fs.put(file, filename=file.filename, content_type=file.content_type)
            file_ids.append(str(file_id))
        except errors.PyMongoError as e:
            return jsonify({'error': str(e)}), 500

    try:
        existing_image_set = db.image_sets.find_one({'title': title})
        if existing_image_set:
            db.image_sets.update_one(
                {'title': title},
                {'$push': {'file_ids': {'$each': file_ids}}}
            )
        else:
            db.image_sets.insert_one({
                'title': title,
                'file_ids': file_ids
            })
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Images uploaded successfully', 'file_ids': file_ids}), 200

@images_bp.route('/images/<title>', methods=['GET'])
def get_images_by_title(title):
    try:
        image_set = db.image_sets.find_one({'title': title})
        if not image_set:
            return jsonify({'error': 'No images found with the given title'}), 404

        image_data = []
        for file_id in image_set['file_ids']:
            file = fs.get(ObjectId(file_id))
            image_data.append({
                'id': file_id,
                'filename': file.filename,
                'url': f"/image/{file_id}"
            })
        return jsonify({'images': image_data}), 200
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500

@images_bp.route('/get', methods=['GET'])
def get_images():
    try:
        image_sets = db.image_sets.find().sort('_id', -1).limit(6)
        sets_data = []
        for image_set in image_sets:
            sets_data.append({
                'title': image_set['title'],
                'file_ids': image_set['file_ids']
            })
        return jsonify({'image_sets': sets_data}), 200
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500

@images_bp.route('/image_get_fileid', methods=['POST'])
def image_fileid_get():
    try:
        data = request.get_json()
        file_id = data['file_id']
        
        file = fs.get(ObjectId(file_id))
        return send_file(BytesIO(file.read()), mimetype=file.content_type, as_attachment=False, download_name=file.filename)
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500
    except KeyError:
        return jsonify({'error': 'File ID is required'}), 400
