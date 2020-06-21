import os
import pprint

import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

import pickle

pp = pprint.PrettyPrinter(indent=2)

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "src\client_secret.json"

# This access scope grants read-only access to the authenticated user's Drive
# account.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
# API_SERVICE_NAME = 'drive'
API_SERVICE_NAME = 'sheets'
API_VERSION = 'v4'


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)

    
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
    else:
        credentials = flow.run_local_server()
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
        
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def list_drive_files(service, **kwargs):
    results = service.files().list(
        **kwargs
    ).execute()
#   results = service.open("Render Rob")

    pp.pprint(results)


def copy_sheet(service):
    service.files().create().execute()
    sheet = service.spreadsheets()
    sheet.create()
    template_id = "1Hc74LRRvTiekuYtiTYaZGC9qCOjnf9SiAurZwmgZjUQ"


def get_sheets(service):
    template_id = "1Hc74LRRvTiekuYtiTYaZGC9qCOjnf9SiAurZwmgZjUQ"
    SAMPLE_RANGE_NAME = 'A1:B2,majorDimension=COLUMNS'

    # print(service.spreadsheets().sheets().copyTo(
        # spreadsheetId=template_id, sheetId=0, body=None, x__xgafv=None))
    # print(service.spreadsheets().create())
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=template_id,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))



if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    #   os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    service = get_authenticated_service()
#   list_drive_files(service,
#                    orderBy='modifiedByMeTime desc',
#                    pageSize=5)
#   copy_sheet(service)
    get_sheets(service)
