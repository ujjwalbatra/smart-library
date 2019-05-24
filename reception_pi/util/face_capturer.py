"""
Part of the face recognition util, captures images of a user's face
"""

import os
import cv2


class FaceCapturer():
    """
    Catures an image of a users face and stores it in the dataset directory
    """

    def __init__(self):
        self.__dataset = 'dataset'
        self.__user = ''
        self.__classifier = 'reception_pi/util/haarcascade_frontalface_default.xml'

        self.__camera = None

    def capture_user_face(self, user):
        """
        Captures and saves an image of the users face, cropped using face detection

        Args:
            user: name of the user to save image under
        """

        folder = "./{}/{}".format(self.__dataset, user)

        # Create a new folder for the new name
        if not os.path.exists(folder):
            os.makedirs(folder)

        self.__start_camera()

        face_detector = cv2.CascadeClassifier(self.__classifier)

        img_counter = 0
        while img_counter <= 10:
            key = input("Press q to quit or ENTER to continue: ")
            if key == "q":
                break

            ret, frame = self.__camera.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)

            if faces != () and faces.size == 0:
                print("No face detected, please try again")
                continue

            for (x, y, w, h) in faces:
                img_name = "{}/{:04}.jpg".format(folder, img_counter)
                cv2.imwrite(img_name, frame[y : y + h, x : x + w])
                print("{} written!".format(img_name))
                img_counter += 1

        self.close()

    def close(self):
        """
        Releases the camera feed
        """

        self.__camera.release()

    def __start_camera(self):
        self.__camera = cv2.VideoCapture(0)

        # Set video width
        self.__camera.set(3, 640)
        # Set video height
        self.__camera.set(4, 480)
