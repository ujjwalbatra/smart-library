from imutils.video import VideoStream
from pyzbar import pyzbar
import datetime
import imutils
import time
import cv2

class QrReader():
    def __init__(self):
        print("[INFO] starting video stream...")
        self.__video_stream = VideoStream(src = 0).start()

        #Allow time for video stream to start up
        time.sleep(2.0)

    def find_codes_with_timeout(self, timeout: int):
        """
        Searches for qr codes until one is detected or the search timeouts

        Args:
            timeout: time in seconds before the search timeouts

        Returns:
            array: an array of string decoded from qr codes, is empty if no codes are found
        """

        start_time = time.time()

        while True:
            frame = self.__video_stream.read()
            frame = imutils.resize(frame, width = 400)

            barcodes = pyzbar.decode(frame)

            if len(barcodes) > 0:
                return list(map(self.__decode_barcode, barcodes))

            elapsed_time = time.time() - start_time

            if elapsed_time > timeout:
                return []

            time.sleep(1)

    def __decode_barcode(self, barcode):
        return barcode.data.decode("utf-8")
