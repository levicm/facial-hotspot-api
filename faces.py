import face_recognition as fr
import numpy as np
import cv2

def extract_encodings(photo_bytes):
    image_np = np.frombuffer(photo_bytes, dtype=np.uint8)
    img_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
    boxes = fr.face_locations(rgb, model='hog')
    return fr.face_encodings(rgb, boxes)

def match_face(known_encodings, unknown_encoding):
    matches = fr.compare_faces(known_encodings, unknown_encoding)
    print(matches)
    if True in matches:
        face_distances = fr.face_distance(known_encodings, unknown_encoding)
        print(face_distances)
        best_match_index = np.argmin(face_distances)
        print(best_match_index)
        if matches[best_match_index]:
            return best_match_index
        else:
            first_match_index = matches.index(True)
            return first_match_index
    return -1

def serialize(nparray):
    return np.array2string(nparray, max_line_width=2500)[1:-1].replace('  ', ' ')

def desserialize(arraystr):
    return np.fromstring(arraystr, count=128, sep=' ')
