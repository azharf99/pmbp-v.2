import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def decode_base64_image(data_url):
    header, encoded = data_url.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    np_img = np.frombuffer(image_bytes, np.uint8)
    np_img = face_recognition.load_image_file(BytesIO(image_bytes))
    return np_img

def encode_face(image_array):
    rgb_image = image_array[:, :, :3]
    face_locations = face_recognition.face_locations(rgb_image)
    if face_locations:
        try:
            encodings = face_recognition.face_encodings(rgb_image, face_locations)
            return encodings  # list of face encodings
        except TypeError as e:
            print("Encoding error:", e)
    return []

def compare_faces(known_encodings, face_encoding):
    matches = face_recognition.compare_faces(known_encodings, face_encoding)
    face_distances = face_recognition.face_distance(known_encodings, face_encoding)
    try:
        best_match_index = np.argmin(face_distances)
        print("known_encodings:", known_encodings)
        print("face_encoding:", face_encoding)
        print("matches:", matches)
        print("face_distance:", face_distances)
        print("best_match_index:", best_match_index)
        if matches[best_match_index]:
            return best_match_index
    except:
        print("known_encodings:", known_encodings)
        print("face_encoding:", face_encoding)
        print("matches:", matches)
        print("face_distance:", face_distances)
    return None