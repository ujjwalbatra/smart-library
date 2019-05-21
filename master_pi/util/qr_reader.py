"""
Provides the QrReader class for reading qr codes
"""

import time
import imutils
from imutils.video import VideoStream
from pyzbar import pyzbar


class QrReader():
    """
    Uses the camera to search for qr codes and decodes them to strings
    """

    def __init__(self):
        self.__video_stream = None

    def start(self):
        """
        Starts the camera and waits for it to warm up
        """

        self.__video_stream = VideoStream(src=0).start()

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
        found_codes = []

        while True:
            frame = self.__video_stream.read()
            frame = imutils.resize(frame, width=400)

            barcodes = pyzbar.decode(frame)

            if barcodes:
                found_codes = list(map(self.__decode_barcode, barcodes))
                break

            elapsed_time = time.time() - start_time

            if elapsed_time > timeout:
                break

            time.sleep(1)

        self.__video_stream.stop()
        return found_codes

    @staticmethod
    def __decode_barcode(barcode):
        """
        Decodes the binary data retrieved from a barcode into utf-8

        Returns:
            string: the decoded binary data
        """

        return barcode.data.decode("utf-8")

    def close(self):
        """
        Releases the camera feed
        """

        self.__video_stream.stop()
