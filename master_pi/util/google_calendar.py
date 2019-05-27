"""
provides functionality of creating calendar events
Acknowledgement: Copyright of https://developers.google.com/calendar/create-events
    used for educational learning only
"""

from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleCalendar(object):
    """
    provides functionality of creating calendar events
    """

    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.__service = self.__authenticate_user()

    def __authenticate_user(self):
        """
        Authenticates user using Google oauth2.
        Google oauth2 Documentation: https://developers.google.com/identity/protocols/OAuth2
        """

        credentials = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                credentials = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)

        service = build('calendar', 'v3', credentials=credentials)

        return service

    def create_event(self, username: str, book_id: int, type_: str, date: datetime.date):
        """
        Creates a google calendar event.

        Args:
            username: username of the library account which event is concerned about
            book_id: id of the book
            type_: can be either book_issued or book_return_date
            date: date of the event
        """

        summary = "username = {}\ntype = {}".format(username, type_)
        description = "type = {}\nid = {}".format(type_, book_id)

        event = {
            'summary': summary,
            'location': '124 La Trobe St, Melbourne VIC 3000',
            'description': description,
            'start': {
                'date': date.__str__(),
                'timeZone': "UTC",
            },
            'end': {
                'date': date.__str__(),
                'timeZone': "UTC",
            },
        }

        self.__service.events().insert(calendarId='primary', body=event).execute()


if __name__ == '__main__':
    GoogleCalendar().create_event("12", 1, "   we", datetime.date.today())
