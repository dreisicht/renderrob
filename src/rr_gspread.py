# import configparser
import os
import sys
import pickle
import webbrowser

from sty import fg, bg, ef, rs, Style, RgbBg
import sty

import google.oauth2.credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime

SHEETNAME = 'Render Rob 2.0'
TEMPLATE_ID = "1prG29lIic0Qqc_fGq5sLdnDh1u8Nkd45MxdaCuRp1Rw"
CLIENT_SECRETS_FILE = "src/client_secret.json"

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


def print_info_input(ipt_str):
    bg.dark_blue = Style(
        RgbBg(69, 129, 142))
    time_current = "[{}]".format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    input(bg.dark_blue + fg.white + time_current +
          "[INFO] " + ipt_str + " press Enter to continue." + rs.all)


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, ['https://www.googleapis.com/auth/drive.file'])

    if os.path.exists('src/util/token.pickle'):
        with open('src/util/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
    else:
        creds = flow.run_local_server()
        with open('src/util/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)


def create_sheet(service):
    spreadsheet = {
        'properties': {
            'title': SHEETNAME,
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                fields='spreadsheetId').execute()
    print('Created Spreadsheet with ID: {0}'.format(
        spreadsheet.get('spreadsheetId')))
    webbrowser.open(
        "https://docs.google.com/spreadsheets/d/" + spreadsheet.get('spreadsheetId'))
    webbrowser.open(
        "https://docs.google.com/spreadsheets/d/" + TEMPLATE_ID)
    return spreadsheet.get('spreadsheetId')


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


def get_values(service, spreadsheetId, range):
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, majorDimension="ROWS",
                                                 range=range).execute()
    values = result.get('values', [])
    return values


def query_sheet():
    # get service
    service_sheets = get_authenticated_service()

    try:
        sheetcache = open("src/util/sheetcache", "r")
        spreadsheetId = sheetcache.read()
        sheetcache.close()
    except FileNotFoundError:
        spreadsheetId = create_sheet(service_sheets)
        sheetcache = open("src/util/sheetcache", "x")
        sheetcache.write(spreadsheetId)
        sheetcache.close()
        print_info_input(
            "Created the Render Rob Spreadsheet. Please copy both sheets from the template sheet to the newly created one. If you copied them")
        cleanup_sheet(service_sheets, spreadsheetId)

    jobs_values = get_values(service_sheets, spreadsheetId, "jobs!A1:V81")
    globals_values = get_values(service_sheets, spreadsheetId, "globals!A1:C7")
    return jobs_values, globals_values


def cleanup_sheet(service, spreadsheetId):
    # get list of sheets
    sheet_metadata = service.spreadsheets().get(
        spreadsheetId=spreadsheetId).execute()
    sheets = sheet_metadata.get('sheets', '')

    for i in range(len(sheets)):
        title = sheets[i].get("properties", {}).get("title")
        sheet_id = sheets[i].get("properties", {}).get("sheetId")
        print(title)
        if "jobs" in title and title != "jobs":
            renameSheet(service, spreadsheetId, sheet_id, "jobs")
            title = "jobs"
        elif "globals" in title and title != "globals":
            renameSheet(service, spreadsheetId, sheet_id, "globals")
            title = "globals"
        elif title != "jobs" and title != "globals":
            delete_sheet(service, spreadsheetId, sheet_id)


if __name__ == "__main__":
    # print(os.getcwd())
    print(query_sheet())
    # read_as_service_account()
    # query_files()
