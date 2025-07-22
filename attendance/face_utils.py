from deepface import DeepFace
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def decode_base64_image(data_url):
    image_bytes = base64.b64decode(data_url)
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    return np.array(image)


def extract_face_embeddings(image_array):
    try:
        analysis = DeepFace.represent(img_path=image_array, enforce_detection=False)
        embeddings = [np.array(face['embedding']) for face in analysis]
        return embeddings
    except Exception as e:
        print(f"Embedding extraction error: {e}")
        return []

def compare_embeddings(known_embeddings, target_embedding, threshold=0.6):
    """
    Compare a target embedding against known embeddings.
    Return index of matching embedding if found, else None.
    """
    if known_embeddings or target_embedding:
        for idx, known in enumerate(known_embeddings):
            distance = np.linalg.norm(known - target_embedding)
            if distance < threshold:
                return idx
    return None