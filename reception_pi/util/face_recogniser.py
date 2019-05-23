"""
Part of the face recognition util, responsible for recognising faces
"""

import pickle
import time
import imutils
from imutils.video import VideoStream
import face_recognition
import cv2

class FaceRecogniser():
    """
    Detects and matches faces to already encoded faces
    """

    def __init__(self):
        self.__encodings = 'encodings.pickle'
        self.__resolution = 240
        self.__detection_method = 'hog'

        self.__video_stream = None
        self.__data = {}

    def find_and_identify_faces_with_timeout(self, timeout):
        """
        Tries to find faces in the camera feed and identifies them if found

        Args:
            timeout: time in seconds before the search timeouts

        Returns:
            array: an array of the names of identified faces, will return empty if search timeouts
        """

        print("[INFO] loading encodings...")
        self.__data = pickle.loads(open(self.__encodings, "rb").read())

        names = []

        encoded_faces = self.__find_encoded_faces_with_timeout(timeout)

        for encoded_face in encoded_faces:
            identified_name = self.__identify_encoding(encoded_face)
            if identified_name:
                names.append(identified_name)

        return names

    def __start_camera(self):
        self.__video_stream = VideoStream(src=0).start()
        time.sleep(2.0)

    def __get_rgb_image(self):
        image = self.__video_stream.read()

        # convert the input frame from BGR to RGB then resize it to have
        # a width of 750px (to speedup processing)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(image, width=self.__resolution)
        return rgb

    def __find_encoded_faces_with_timeout(self, timeout):
        print("[INFO] starting video stream...")
        self.__start_camera()

        start_time = time.time()

        while True:
            rgb_image = self.__get_rgb_image()
            encoded_faces = self.__encode_faces(rgb_image)

            if encoded_faces:
                self.__video_stream.stop()
                return encoded_faces

            elapsed_time = time.time() - start_time.time()

            if elapsed_time > timeout:
                return []

    def __encode_faces(self, image):
        boxes = face_recognition.face_locations(image, model=self.__detection_method)
        encodings = face_recognition.face_encodings(image, boxes)
        return encodings

    def __identify_encoding(self, encoded_face):
        matches = face_recognition.compare_faces(self.__data["encodings"], encoded_face)
        name = None

        if True in matches:
            matched_indices = [index for (index, isMatched) in enumerate(matches) if isMatched]
            counts = {}

            for i in matched_indices:
                name = self.__data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            name = max(counts, key=counts.get)

        return name
