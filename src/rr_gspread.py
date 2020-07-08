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
from googleapiclient.errors import HttpError

SHEETNAME = 'Render Rob 2.0'
TEMPLATE_ID = "1prG29lIic0Qqc_fGq5sLdnDh1u8Nkd45MxdaCuRp1Rw"
CLIENT_SECRETS_FILE = "src/client_secret.json"
DOCS_URI = "https://docs.google.com/spreadsheets/d/"

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


def print_error(ipt_str):
    time_current = "[{}]".format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    bg.red = Style(RgbBg(152, 0, 48))
    input(bg.red + fg.white + time_current +
          " [ERROR] " + ipt_str + " Press Enter to exit." + rs.all)
    sys.exit()


def print_warning(ipt_str):
    time_current = "[{}]".format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    bg.yellow = Style(RgbBg(255, 217, 102))
    input(bg.yellow + fg.black + time_current +
          "[WARNING] " + ipt_str + " Press Enter to continue." + rs.all)


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
    # print('Created Spreadsheet with ID: {0}'.format(
    #     spreadsheet.get('spreadsheetId')))
    webbrowser.open(
        DOCS_URI + TEMPLATE_ID)
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


def get_sheets(service, spreadsheetId):
    sheet_metadata = service.spreadsheets().get(
        spreadsheetId=spreadsheetId).execute()
    return sheet_metadata.get('sheets', '')


def cleanup_sheet(service, spreadsheetId):
    sheets = get_sheets(service, spreadsheetId)
    for i in range(len(sheets)):
        title = sheets[i].get("properties", {}).get("title")
        sheet_id = sheets[i].get("properties", {}).get("sheetId")
        if sheet_id == 0 and len(sheets) == 1:
            os.remove("src/util/sheetcache")
            print_error("Your sheet is empty. Next time you launch me, I will start from the beginning. " +
                  DOCS_URI + spreadsheetId)
        if "jobs" in title and title != "jobs":
            renameSheet(service, spreadsheetId, sheet_id, "jobs")
            title = "jobs"
        elif "globals" in title and title != "globals":
            renameSheet(service, spreadsheetId, sheet_id, "globals")
            title = "globals"
        elif len(sheets) == 1:
            os.remove("src/util/sheetcache")
            print_error("Something went terribly wrong. I will create a new sheet if you launch me again.")
        elif title != "jobs" and title != "globals":
            delete_sheet(service, spreadsheetId, sheet_id)


def get_values(service, spreadsheetId, value_range):
    for _ in range(2):
        try:
            result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, majorDimension="ROWS",
                                                         range=value_range).execute()
        except HttpError as eh:
            if "Unable to parse range" in eh._get_reason():
                cleanup_sheet(service, spreadsheetId)
            if "not found" in eh._get_reason():
                os.remove("src/util/sheetcache")
                print_error(
                    "I couldn't find the sheet. Are you sure you didn't delete it?")
        else:
            break
    else:
        print("Please check your sheet, if it cointains a globals and a jobs sheet: " +
              DOCS_URI + spreadsheetId)
        sys.exit()

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
            "Created the Render Rob Spreadsheet. Please copy both 'jobs' and 'globals' sheet from the \
                                            template to the newly created document. If you copied them")
        for _ in range(3):
            sheets = get_sheets(service_sheets, spreadsheetId)
            if len(sheets) < 3:
                print_warning(
                    "I'm sorry, but you didn't copy both sheets to the new spreadsheet. Please try again!")
            else:
                break
        else:
            # os.remove("src/util/sheetcache")
            print_error(
                "To be honest, we were never supposed to land here. Please try Running Render Rob again!")
        cleanup_sheet(service_sheets, spreadsheetId)
        webbrowser.open(DOCS_URI + spreadsheetId)
        print_info_input(
            "I opened the spreadsheet and I'll let you fill it out. If you're done")

    jobs_values = get_values(service_sheets, spreadsheetId, "jobs!A1:V81")
    globals_values = get_values(service_sheets, spreadsheetId, "globals!A1:C7")
    return jobs_values, globals_values


if __name__ == "__main__":
    print(query_sheet())
