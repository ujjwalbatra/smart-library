"""
provides speech to text utility using google api
"""

import json
import subprocess

import speech_recognition as sr


class VoiceSearch(object):
    """
    provides speech to text utility using google api
    """

    def __init__(self):
        self.__mic_name = self.__get_mic_details()
        self.__api_key = self.__get_api_key()

    def __get_mic_details(self):
        """
        Gets details of recording hardware form config.json

        Returns:
            string: name of the mic
        """

        with open('./master_pi/config.json') as json_file:
            data = json.load(json_file)
            return data['mic_name']

    def __get_api_key(self):
        """
        Gets api key for speech to text form config.json

        Returns:
            string: api key
        """

        with open('./master_pi/config.json') as json_file:
            data = json.load(json_file)
            return data['voice_api_key']

    def get_voice_input(self, message: str):
        """
        Listens to users voice input and converts it to text

        Args:
            message: message to print before listing

        Returns:
            string: text of the speech input

        """
        # Set the device ID of the mic that we specifically want to use to avoid ambiguity
        for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
            if microphone_name == self.__mic_name:
                device_id = i
                break

        # obtain audio from the microphone
        r = sr.Recognizer()
        with sr.Microphone(device_index=device_id) as source:
            # clear console of errors
            subprocess.run("clear")

            # wait for a second to let the recognizer adjust the
            # energy threshold based on the surrounding noise level
            r.adjust_for_ambient_noise(source)

            print(message)
            try:
                audio = r.listen(source, timeout=2.5)
            except sr.WaitTimeoutError:
                print("Listening timed out whilst waiting for voice")
                return None

        # recognize speech using Google Speech Recognition
        voice_input = None
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            voice_input = r.recognize_google(audio)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        finally:
            return voice_input
