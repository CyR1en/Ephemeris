import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from util import client_secret, token_dest


class GoogleService:
    def __init__(self, app_ctx):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.events']
        self._cred_path = client_secret(app_ctx)
        self._token_path = token_dest()
        self._credentials = None
        self.resource = None

    def get_resource(self):
        return self.resource

    def is_token_exists(self):
        return os.path.exists(self._token_path)

    def is_credentials_valid(self):
        return self._credentials and self._credentials.valid

    def build_resource(self):
        self.resource = build('calendar', 'v3', credentials=self._credentials)

    def insert_event(self, event):
        return self.resource.events().insert(calendarId='primary', body=event).execute()

    def prepare_credentials(self):
        if self.is_token_exists():
            self._credentials = Credentials.from_authorized_user_file(self._token_path, self.SCOPES)

        if not self.is_credentials_valid():
            if self._credentials and self._credentials.expired and self._credentials.refresh_token:
                self._credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self._cred_path, self.SCOPES)
                self._credentials = flow.run_local_server(port=0)
            with open(self._token_path, 'w') as token:
                token.write(self._credentials.to_json())
