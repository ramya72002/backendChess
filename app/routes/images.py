from flask import Blueprint, request, jsonify, send_file
from app.database import db, fs
from bson import ObjectId
from io import BytesIO
from pymongo import errors

images_bp = Blueprint('images', __name__)

 
@images_bp.route('/upload', methods=['POST'])
def upload_image():
    # Check for required fields in the request
    if 'images' not in request.files or 'title' not in request.form or 'level' not in request.form:
        return jsonify({'error': 'Missing required fields in the request'}), 400
    
    level = request.form['level']
    category = request.form["category"]
    title = request.form['title']
    live = request.form['live']
    date_time = request.form['date_time']
    
    # Get puzzle number from the request or default to 1 if not provided
    puzzle_number = request.form.get('puzzle_number', '1')
    
    files = request.files.getlist('images')
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400

    file_ids_dict = {}
    try:
        for i, file in enumerate(files):
            file_id = fs.put(file, filename=file.filename, content_type=file.content_type)
            puzzle_key = f'puzzle{puzzle_number}'  # Use puzzle_number to create the key
            file_ids_dict[puzzle_key] = {
                'id': str(file_id),
                'solution': 'solution_placeholder',  # Placeholder, update as needed
                'sid_link': 'link_placeholder'  # Placeholder, update as needed
            }
    except Exception as e:
        return jsonify({'error': f'Failed to upload file: {str(e)}'}), 500

    try:
        existing_image_set = db.image_sets.find_one({
            'title': title,
            'level': level,
            'category': category,
            'live': live,
            'date_time': date_time
        })

        if existing_image_set:
            print("Existing image set found, updating...")
            print(f"Existing file_ids: {existing_image_set.get('file_ids', {})}")
            updated_file_ids = existing_image_set.get('file_ids', {})
            updated_file_ids.update(file_ids_dict)
            print(f"Updated file_ids: {updated_file_ids}")
            
            update_result = db.image_sets.update_one(
                {'title': title, 'level': level, 'category': category, 'live': live, 'date_time': date_time},
                {'$set': {'file_ids': updated_file_ids}}
            )
            print(f"Update Result: {update_result.modified_count} document(s) modified.")
        else:
            print("No existing image set found, inserting new record...")
            db.image_sets.insert_one({
                'level': level,
                'title': title,
                'category': category,
                'live': live,
                'date_time': date_time,
                'file_ids': file_ids_dict
            })
    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({'message': 'Images uploaded successfully', 'file_ids': file_ids_dict}), 200



@images_bp.route('/getpuzzleid', methods=['GET'])
def get_puzzle():
    level = request.args.get('level')
    category = request.args.get('category')
    title = request.args.get('title')
    live = request.args.get('live')
    puzzle_number = request.args.get('puzzle_number')

    if not (level and category and title and live and puzzle_number):
        return jsonify({'error': 'Missing required parameters'}), 400

    # Construct the query to find the image set
    query = {
        'level': level,
        'category': category,
        'title': title,
        'live': live
    }

    try:
        image_set = db.image_sets.find_one(query)
        if not image_set:
            return jsonify({'error': 'Image set not found'}), 404
        
        # Extract the file_ids and puzzle info
        puzzle_info = image_set.get('file_ids', {}).get(f'puzzle{puzzle_number}', {})
        
        response = {
            'level': image_set.get('level'),
            'category': image_set.get('category'),
            'title': image_set.get('title'),
            'live': image_set.get('live'),
            'date_time': image_set.get('date_time'),
            'puzzle': {
                'id': puzzle_info.get('id'),
                'solution': puzzle_info.get('solution'),
                'sid_link': puzzle_info.get('sid_link')
            }
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': f'Error retrieving puzzle data: {str(e)}'}), 500


@images_bp.route('/get_puzzle_sol', methods=['PUT'])
def update_puzzle_sol():
    # Extract data from request
    data = request.json
    level = data.get('level')
    category = data.get('category')
    title = data.get('title')
    live = data.get('live')
    column_name = data.get('column_name')
    sid_link = data.get('sid_link')
    solution = data.get('solution')

    if not all([level, category, title, live, column_name, sid_link, solution]):
        return jsonify({'error': 'Missing required fields in the request'}), 400

    # Build the update query
    update_query = {
        '$set': {
            f'file_ids.{column_name}.sid_link': sid_link,
            f'file_ids.{column_name}.solution': solution
        }
    }

    # Find and update the document
    try:
        result = db.image_sets.update_one(
            {
                'title': title,
                'level': level,
                'category': category,
                'live': live
            },
            update_query
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'No matching document found'}), 404
        
        return jsonify({'message': 'Puzzle updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
 


@images_bp.route('/images/<title>', methods=['GET'])
def get_images_by_title(title):
    level = request.args.get('level')
    try:
        # Find the image set by both title and level
        image_set = db.image_sets.find_one({'title': title, 'level': level})
        if not image_set:
            return jsonify({'error': 'No images found with the given title and level'}), 404

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

@images_bp.route('/imagesets', methods=['GET'])
def get_image_sets():
    try:
        # Fetch all records from the image_sets collection, sorted by _id in descending order
        image_sets = list(db.image_sets.find({}).sort('_id', -1))
        
        # Convert ObjectId to string and return all fields
        for image_set in image_sets:
            image_set['_id'] = str(image_set['_id'])  # Convert ObjectId to string
        
        return jsonify(image_sets), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @images_bp.route('/get', methods=['GET'])
# def get_images():
#     try:
#         image_sets = db.image_sets.find().sort('_id', -1).limit(6)
#         sets_data = []
#         for image_set in image_sets:
#             sets_data.append({
#                 # 'level': image_set['level'],
#                 'title': image_set['title'],
#                 'file_ids': image_set['file_ids']
#             })
#         return jsonify({'image_sets': sets_data}), 200
#     except errors.PyMongoError as e:
#         return jsonify({'error': str(e)}), 500


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


