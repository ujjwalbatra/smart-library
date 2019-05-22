from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2

class FaceRecogniser():
    def __init__(self):
        self.__encodings = 'encodings.pickle'
        self.__resolution = 240
        self.__detection_method = 'hog'

        self.__video_stream = None
        self.__data = {}

    def find_and_identify_faces(self):
        print("[INFO] loading encodings...")
        self.__data = pickle.loads(open(args["encodings"], "rb").read())

        names = []

        encoded_faces = self.__find_encoded_faces(self)

        for encoded_face in encoded_faces:
            identified_name = self.__identify_encoding(encoded_face)
            if identified_name:
                names.append(name)

        return names

    def __start_camera(self):
        self.__video_stream = VideoStream(src = 0).start()
        time.sleep(2.0)

    def __get_rgb_image(self):
        image = vs.read()

        # convert the input frame from BGR to RGB then resize it to have
        # a width of 750px (to speedup processing)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(image, width = self.__resolution)
        return rgb

    def __find_encoded_faces(self):
        print("[INFO] starting video stream...")
        self.__start_camera()

        while True:
            rgb_image = self.__get_rgb_image()
            encoded_faces = self.__encode_faces(rgb_image)

            if encoded_faces:
                vs.stop()
                return encoded_faces

    def __encode_faces(self, image):
        boxes = face_recognition.face_locations(image, model = self.__detection_method)
        encodings = face_recognition.face_encodings(image, boxes)
        return encodings

    def __identify_encoding(self, encoded_face):
        matches = face_recognition.compare_faces(self.__data["encodings"], encoded_face)
        name = None

        if True in matches:
            matchedIndices = [index for (index, isMatched) in enumerate(matches) if isMatched]
            counts = {}

            for i in matchedIndices:
                name = self.__data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            name = max(counts, key = counts.get)
