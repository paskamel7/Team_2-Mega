import cv2
import face_recognition
import numpy as np
import base64
from io import BytesIO
from flask import Flask, request, jsonify,render_template
from PIL import Image
import os
import glob
import serial
from flask_cors import CORS

#connection = serial.Serial('COM3', 9600)  

class facerec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resize = 0.25

    def encodings_imgs(self, images_path):
        images_path = glob.glob(os.path.join(images_path, "*.*"))
        for path in images_path:
            img = cv2.imread(path)
            rgb_path = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            basename = os.path.basename(path)
            (filename, ext) = os.path.splitext(basename)
            encodingss = face_recognition.face_encodings(rgb_path)
            if encodingss:  
                self.known_face_encodings.append(encodingss[0])
                self.known_face_names.append(filename)

    def detect(self, frame):
        sm_frame = cv2.resize(frame, (0, 0), fx=self.frame_resize, fy=self.frame_resize)
        rgb_frame = cv2.cvtColor(sm_frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, locations)
        face_names = []
        for f_e in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, f_e)
            if True in matches:
                match_in = matches.index(True)
                name = self.known_face_names[match_in]
            else:
                name = "Unknown"
            face_names.append(name)
        face_locations = np.array(locations)
        face_locations = face_locations / self.frame_resize
        return face_locations.astype(int), face_names

    def detect_face(self, image):
        rgb_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        return len(face_locations) > 0

face_recognition_service = facerec()
face_recognition_service.encodings_imgs('images')

app = Flask(__name__)
CORS(app) 
new_password = "1234"
@app.route('/')
def index():
    return render_template('faceRec.html')
# Directory to save images
IMAGE_DIR = 'static/images'
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

@app.route('/homeRes', methods=['POST'])
def homeRes():
    try:
        data = request.get_json()
        img_data = data.get('image')

        if img_data:
            # Process the base64-encoded image
            img_data = img_data.replace('data:image/png;base64,', '')
            img_bytes = base64.b64decode(img_data)
            image = Image.open(BytesIO(img_bytes))
             # Convert image to RGB if it is in RGBA mode
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            # Save the image with a default name
            file_path = os.path.join(IMAGE_DIR, 'unknown_face.jpg')
            image.save(file_path)

            return jsonify({'redirect_url': url_for('homeOwners', img_path='images/unknown_face.jpg')})

        return jsonify({'error': 'No image data provided'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/homeowner')
def homeOwners():
    img_path = request.args.get('img_path', 'images/unknown_face.jpg')
    return render_template('owners.html', src=img_path)

@app.route('/decision-action', methods=['POST'])
def decisionAction():
    try:
        action = request.form.get('action')
        img_path = request.form.get('img_path')
        name = request.form.get('name', 'unknown')

        if action == 'open':
          
            return jsonify({'message': 'Door opened!'})

        elif action == 'add_and_open':
            # Save the image with the given name
            new_path = os.path.join('images', f'{name}.jpg')
            os.rename(os.path.join(IMAGE_DIR, 'unknown_face.jpg'), new_path)
          
            face_recognition_service.encodings_imgs('images')
            return jsonify({'message': f'Door opened and {name} added to the system!'})

        return jsonify({'error': 'Invalid action'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_password', methods=['POST'])
def check_password():
    data = request.get_json()
    password = data['password']
    if password == new_password:  
        return jsonify({'message': 'Password correct, proceed to add user.'})
    else:
        return jsonify({'message': 'Incorrect password.'}), 400
@app.route('/change_password', methods=['POST'])
def change_password():
    if request.method == 'POST':
        data = request.get_json()
        new_password = data['new_password']
        #connection.write(new_password.encode())  
        return jsonify({'status': 'Password updated', 'new_password': new_password})
@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('name')
    img = request.files.get('img')

    if not name or not img:
        return jsonify({'message': 'Name or image file is missing.'}), 400

    img_data = img.read()
    image = Image.open(BytesIO(img_data))
    
    if face_recognition_service.detect_face(np.array(image)):
        file_path = os.path.join('images', f'{name}.jpg')
        image.save(file_path)
        face_recognition_service.encodings_imgs('images')
        return jsonify({'message': 'User added successfully.'})
    else:
        return jsonify({'message': 'No face detected in the image.'}), 400
@app.route('/recognize_face', methods=['POST'])
def recognize_face():
    if request.method == 'POST':
        data = request.get_json()
        img_data = data['image']
        img_data = img_data.replace('data:image/png;base64,', '')
        img_bytes = base64.b64decode(img_data)
        image = Image.open(BytesIO(img_bytes))
        face_locations, face_names = face_recognition_service.detect(np.array(image))
        if face_names:
            name = face_names[0]  
            #if name!= "Unknown":
                 #connection.write(b'1')
        else: 
            name = 'Unknown'
            while True:
                command = input("Enter 'Open' if u want to open only and press 'Add' if u want to open and add ")
                if command == "Open":
                    #connection.write(b'1')
                    #break
                #elif command == "Add":
                    #connection.write(b'1')
                    #add_user()
                    #break
                #else:
                    print("Please Enter The correct command")
        return jsonify({"name": name, "face_locations": face_locations.tolist()})
    elif request.method == 'GET':
        return jsonify({'message': 'Please send a POST request with a base64-encoded image to recognize faces.'})
     
@app.route('/delete_user', methods=['POST', 'GET'])
def delete_user():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name') 
        
        if not name:
            return jsonify({'message': 'No name provided in request.'}), 400
        
        # List of possible image formats
        possible_extensions = ['.jpg', '.jpeg', '.png']
        file_deleted = False
        
        for ext in possible_extensions:
            file_path = os.path.join('images', f'{name}{ext}')
            if os.path.exists(file_path):
                os.remove(file_path)  # Remove user image file
                file_deleted = True
                break
        
        if file_deleted:

            return jsonify({'status': 'success', 'message': f'User {name} deleted successfully.'})
        else:
            return jsonify({'status': 'error', 'message': f'User {name} not found.'}), 404
    
    elif request.method == 'GET':
        return jsonify({'message': 'Please send a POST request to delete a user.'})
if __name__ == "__main__":
    app.run(debug=True)
