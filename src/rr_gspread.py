# import configparser
import os
import sys
import pickle
import webbrowser

import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from datetime import datetime

SHEETNAME = 'Render Rob 2.0'

CLIENT_SECRETS_FILE = "src\client_secret.json"

# This access scope grants read-only access to the authenticated user's Drive
# account.
SCOPES = ['https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/spreadsheets.readonly']
# API_SERVICE_NAME = 'drive'
API_SERVICE_NAME = 'sheets'
API_VERSION = 'v4'


def print_info(ipt_str):
    time_current = "[{}]".format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(time_current, ipt_str)


def get_sheet_name():
    current_path = os.path.dirname(
        os.path.realpath(__file__)).replace("\\", "/")+"/"
    try:
        f_ini = open(current_path + "user/sheetname.ini", "r")
        sheetname = f_ini.read()
        f_ini.close()
    except FileNotFoundError:
        sheetname = SHEETNAME


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)

    if os.path.exists('src/util/token.pickle'):
        with open('src/util/token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
    else:
        credentials = flow.run_local_server()
        with open('src/util/token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def create_sheet(service):
    spreadsheet = {
        'properties': {
            'title': SHEETNAME
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                fields='spreadsheetId').execute()
    print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))
    return spreadsheet.get('spreadsheetId')


def copy_sheet(service):
    template_id = "1Hc74LRRvTiekuYtiTYaZGC9qCOjnf9SiAurZwmgZjUQ"
    new_spreadsheet_id = create_sheet(service)

    dest_body = {
        'destination_spreadsheet_id': new_spreadsheet_id,
    }

    jobs_sheet = service.spreadsheets().sheets().copyTo(
        spreadsheetId=template_id, sheetId=0, body=dest_body).execute()
    jobs_sheet_id = jobs_sheet.get("sheetId")
    renameSheet(service, new_spreadsheet_id, jobs_sheet_id, "jobs")

    globals_sheet = service.spreadsheets().sheets().copyTo(
        spreadsheetId=template_id, sheetId=1436513898, body=dest_body).execute()
    globals_sheet_id = globals_sheet.get("sheetId")
    renameSheet(service, new_spreadsheet_id, globals_sheet_id, "globals")

    delete_sheet(service, new_spreadsheet_id, 0)

    webbrowser.open(
        "https://docs.google.com/spreadsheets/d/" + new_spreadsheet_id)

    return new_spreadsheet_id


def batch(service, spreadsheetId, requests):
    body = {
        'requests': requests
    }
    return service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()


def renameSheet(service, spreadsheetId, sheetId, newName):
    return batch(service, spreadsheetId, {
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheetId,
                "title": newName,
            },
            "fields": "title",
        }
    })


def hide_sheet(service, spreadsheetId, sheetId):
    return batch(service, spreadsheetId, {
        "updateSheetProperties": {
            "properties": {
                'sheetId': sheetId,
                'hidden': True
            },
            "fields": "title",
        }
    })


def delete_sheet(service, spreadsheetId, sheetId):
    return batch(service, spreadsheetId, {
        "deleteSheet": {
            "sheetId": sheetId
        }
    }
    )

# def get_sheet_id_by_name(service):
#     spreadsheet = service.spreadsheets().get(
#         spreadsheetId=SPREADSHEET_ID).execute()
#     sheet_id = None
#     for _sheet in spreadsheet['sheets']:
#         if _sheet['properties']['title'] == sheet_name:
#             sheet_id = _sheet['properties']['sheetId']


def get_values(service, spreadsheetId, range):
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, majorDimension="ROWS",
                                                 range=range).execute()
    values = result.get('values', [])
    return values


def query_sheet():
    # get service
    service = get_authenticated_service()

    try:
        sheetcache = open("src/util/sheetcache", "r")
        spreadsheetId = sheetcache.read()
        sheetcache.close()
    except FileNotFoundError:
        spreadsheetId = copy_sheet(service)
        sheetcache = open("src/util/sheetcache", "x")
        sheetcache.write(spreadsheetId)
        sheetcache.close()
        print_info("Created the Render Rob Spreadsheet. Gonna quit for now, so you can fill it with your infomration.")
        sys.exit()

    jobs_values = get_values(service, spreadsheetId, "jobs!A1:V81")
    globals_values = get_values(service, spreadsheetId, "globals!A1:C7")
    return jobs_values, globals_values


if __name__ == "__main__":
    query_sheet()
