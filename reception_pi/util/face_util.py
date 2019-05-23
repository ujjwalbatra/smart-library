"""
Provides the FaceUtil class for registering and identifying faces
"""

from util.face_capturer import FaceCapturer
from util.face_encoder import FaceEncoder
from util.face_recogniser import FaceRecogniser

class FaceUtil():
    """
    Provides methods for registering a face during user registration, and identifying faces on login
    """

    def register_face(self, user):
        """
        Captures the user's face, then encodes it under their username

        Args:
            user: the username to save the face under
        """

        face_capturer = FaceCapturer()
        face_capturer.capture_user_face(user)

        face_encoder = FaceEncoder()
        face_encoder.encode_faces()

    def identify_face(self):
        """
        Captures the user's face and matches it against registered users

        Returns:
            array: an array of identified users, or an empty array if no users are recognised
        """

        face_recogniser = FaceRecogniser()
        names = face_recogniser.find_and_identify_faces_with_timeout(5)
        return names


