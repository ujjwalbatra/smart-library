from imutils import paths
import face_recognition
import pickle
import cv2
import os


class FaceReader():
    def __init__(self):
        self.__dataset = 'dataset'
        self.__detection_method = 'hog'
        self.__encodings = 'encodings.pickle'

        self.__knownEncodings = []
        self.__knownNames = []

    def encode_faces(self):
        image_paths = list(paths.list_images(self.__dataset))

        self.__knownEncodings = []
        self.__knownNames = []

        for (i, image_path) in enumerate(image_paths):
            print("[INFO] processing image {}/{}".format(i + 1, len(image_paths)))
            self.__open_and_encode_image(image_path)

        print("[INFO] serializing encodings...")
        self.__serialize_encodings()

    def __open_and_encode_image(self, image_path):
        name = image_path.split(os.path.sep)[-2]

        rgb_image = self.__open_rgb_image(image_path)
        encodings = self.__find_and_encode_faces(rgb_image)
        
        for encoding in encodings:
            self.__knownEncodings.append(encoding)
            self.__knownNames.append(name)

    def __serialize_encodings(self):
        data = {
            "encodings": self.__knownEncodings,
            "names": self.__knownNames 
        }

        with open(self.__encodings) as file:
            file.write(pickle.dumps(data))

    def __open_rgb_image(self, image_path):
        image = cv2.imread(image_path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return rgb

    def __find_and_encode_faces_in(self, image):
        boxes = face_recognition.face_locations(image, model = self.__detection_method)
        encodings = face_recognition.face_encodings(image, boxes)
        return encodings
