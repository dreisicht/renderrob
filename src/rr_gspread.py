# import configparser
import os
import sys
import pickle
import webbrowser

from sty import fg, bg, ef, rs, Style, RgbBg
import sty

from datetime import datetime

import google.oauth2.credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SHEETNAME = 'Render Rob 2.0'
TEMPLATE_ID = "1prG29lIic0Qqc_fGq5sLdnDh1u8Nkd45MxdaCuRp1Rw"
DOCS_URI = "https://docs.google.com/spreadsheets/d/"

CLIENT_SECRET = {
	"installed": {
		"client_id": "243119286709-ceqv1581dilf28n3tiuspu8csj66tv7b.apps.googleusercontent.com",
		"project_id": "renderpipeline",
		"auth_uri": "https://accounts.google.com/o/oauth2/auth",
		"token_uri": "https://oauth2.googleapis.com/token",
		"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
		"client_secret": "iG99SL4rYTUIZC-f9WtdrnKv",
		"redirect_uris": [
			"urn:ietf:wg:oauth:2.0:oob",
			"http://localhost"
		]
	}
}

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
    flow = InstalledAppFlow.from_client_config(
        CLIENT_SECRET, ['https://www.googleapis.com/auth/drive.file'])

    if os.path.exists('cache/token.pickle'):
        with open('cache/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
    else:
        creds = flow.run_local_server()
        with open('cache/token.pickle', 'wb') as token:
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
            os.remove("cache/SHEETCACHE")
            print_error("Your sheet is empty. Next time you launch me, I will start from the beginning. " +
                  DOCS_URI + spreadsheetId)
        if "jobs" in title and title != "jobs":
            renameSheet(service, spreadsheetId, sheet_id, "jobs")
            title = "jobs"
        elif "globals" in title and title != "globals":
            renameSheet(service, spreadsheetId, sheet_id, "globals")
            title = "globals"
        elif len(sheets) == 1:
            os.remove("cache/SHEETCACHE")
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
                os.remove("cache/SHEETCACHE")
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
        sheetcache = open("cache/SHEETCACHE", "r")
        spreadsheetId = sheetcache.read()
        sheetcache.close()
        print_info(f"I'm using this cached spreadsheet: {DOCS_URI + spreadsheetId}")
    except FileNotFoundError:
        spreadsheetId = create_sheet(service_sheets)
        sheetcache = open("cache/SHEETCACHE", "x")
        sheetcache.write(spreadsheetId)
        sheetcache.close()
        print_info_input(
            "I Created a new Render Rob Spreadsheet. Please copy both 'jobs' and 'globals' sheet from the \
                                            template to the newly created document. If you copied them")
        for _ in range(7):
            sheets = get_sheets(service_sheets, spreadsheetId)
            jobs_c = 0
            globals_c = 0
            for sheet in sheets:
                if "jobs" in sheet.get("properties", {}).get("title"):
                    jobs_c += 1
                    if jobs_c > 1:
                        delete_sheet(service_sheets, spreadsheetId,
                                     sheet.get("properties", {}).get("sheetId"))
                        jobs_c = jobs_c -1
                if "globals" in sheet.get("properties", {}).get("title"):
                    globals_c += 1
                    if globals_c > 1:
                        delete_sheet(service_sheets, spreadsheetId,
                                     sheet.get("properties", {}).get("sheetId"))
                        globals_c = globals_c - 1
            # print(jobs_c, globals_c)
            
            if jobs_c != 1 or globals_c != 1:
                print_warning(
                    "I'm sorry, but you didn't copy both sheets to the new spreadsheet. Please try again! If you want to see the sheet, it's here: {}".format(DOCS_URI + spreadsheetId))
            else:
                break
            
        else:
            # os.remove("cache/SHEETCACHE")
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
