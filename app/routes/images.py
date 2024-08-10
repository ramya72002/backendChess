from flask import Blueprint, request, jsonify, send_file
from app.database import db, fs
from bson import ObjectId
from io import BytesIO
from pymongo import errors

images_bp = Blueprint('images', __name__)

@images_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'images' not in request.files or 'title' not in request.form or 'level' not in request.form:
        return jsonify({'error': 'No images or title part in the request'}), 400
    level=request.form['level']
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
        existing_image_set = db.image_sets.find_one({'title': title,'level':level})
        if existing_image_set:
            db.image_sets.update_one(

                {'title': title,'level':level},
                {'$push': {'file_ids': {'$each': file_ids}}}
            )
        else:
            db.image_sets.insert_one({
                'level':level,
                'title': title,
                'file_ids': file_ids
            })
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Images uploaded successfully', 'file_ids': file_ids}), 200

@images_bp.route('/images/<title>', methods=['GET'])
def get_images_by_title(title,level):
    try:
        image_set = db.image_sets.find_one({'title': title,'level':level})
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
                # 'level': image_set['level'],
                'title': image_set['title'],
                'file_ids': image_set['file_ids']
            })
        return jsonify({'image_sets': sets_data}), 200
    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500


@images_bp.route('/get_level', methods=['GET'])
def get_level_images():
    level = request.args.get('level')  # Get the level parameter from the query string
    if not level:
        return jsonify({'error': 'Level parameter is required'}), 400

    try:
        # Query to find image sets that match the specified level
        image_sets = db.image_sets.find({'level': level}).sort('_id', -1)
        
        sets_data = []
        for image_set in image_sets:
            sets_data.append({
                'level': image_set['level'],
                'title': image_set['title'],
                'file_ids': image_set['file_ids']
            })
        
        if not sets_data:
            return jsonify({'message': 'No image sets found for this level'}), 404

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


@images_bp.route('/delete-arena-title', methods=['DELETE'])
def delete_images():
    try:
        data = request.json
        title = data.get('title')
        level = data.get('level')

        print('Received data:', {'title': title, 'level': level})  # Log received data

        if not title or not level:
            return jsonify({'error': 'Title and level are required'}), 400

        # Find the image set to be deleted
        image_set = db.image_sets.find_one({'title': title, 'level': level})
        if not image_set:
            return jsonify({'error': 'No image set found with the specified title'}), 404

        file_ids = image_set.get('file_ids', [])

        # Loop over each file_id and delete related records from fs.files and fs.chunks
        for file_id in file_ids:
            try:
                file_id_obj = ObjectId(file_id)
                
                # Delete the file document from fs.files
                fs_files_delete_result = db.fs.files.delete_one({'_id': file_id_obj})
                
                if fs_files_delete_result.deleted_count == 0:
                    return jsonify({'error': f'File with id {file_id} not found in fs.files'}), 404
                
                # Delete the related chunks from fs.chunks
                fs_chunks_delete_result = db.fs.chunks.delete_many({'files_id': file_id_obj})

            except errors.PyMongoError as e:
                return jsonify({'error': f'Error deleting file or chunks with id {file_id}: {str(e)}'}), 500

        # Delete the entire image set document
        delete_result = db.image_sets.delete_one({'title': title, 'level': level})
        if delete_result.deleted_count == 0:
            return jsonify({'error': 'Failed to delete the image set document'}), 500

        return jsonify({'message': f'Files, chunks, and image set related to title "{title}" have been deleted successfully.'}), 200

    except errors.PyMongoError as e:
        return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


