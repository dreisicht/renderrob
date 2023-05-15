""" This module contains functions to interact with Google Sheets API."""
import os
import pickle
import sys
import webbrowser
from typing import List, Tuple

import rr_print_utils
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SHEETNAME = 'Render Rob 2.0'
TEMPLATE_SHEET_ID = "1prG29lIic0Qqc_fGq5sLdnDh1u8Nkd45MxdaCuRp1Rw"
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
SCOPES = ['https://www.googleapis.com/auth/drive.file']
API_SERVICE_NAME = 'sheets'
API_VERSION = 'v4'


def get_authenticated_service():
  """Gets an authenticated service to access Google Drive API."""
  token_path = "cache/token.pickle"
  if os.path.exists(token_path):
    with open(token_path, 'rb') as token:
      creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
  else:
    flow = InstalledAppFlow.from_client_config(
        CLIENT_SECRET, ['https://www.googleapis.com/auth/drive.file'])
    creds = flow.run_local_server()
    with open(token_path, 'wb') as token:
      pickle.dump(creds, token)

  return build('sheets', 'v4', credentials=creds)


def create_sheet(service, sheet_name: str) -> str:
  """Creates a spreadsheet, returns the newly created spreadsheet ID."""
  spreadsheet = {
      'properties': {
          'title': sheet_name,
      }
  }
  spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                              fields='spreadsheetId').execute()
  return spreadsheet.get('spreadsheetId')


def batch(service, spreadsheet_id, requests):
  """Executes multiple requests in a single batch."""
  body = {
      'requests': requests
  }
  return service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def rename_sheet(service, spreadsheet_id, sheet_id, new_name):
  """Renames a sheet."""
  return batch(service, spreadsheet_id, {
      "updateSheetProperties": {
          "properties": {
              "sheetId": sheet_id,
              "title": new_name,
          },
          "fields": "title",
      }
  })


# def hide_sheet(service, spreadsheet_id, sheet_id):
#   """Sets a sheet to be hidden."""
#   return batch(service, spreadsheet_id, {
#       "updateSheetProperties": {
#           "properties": {
#               'sheetId': sheet_id,
#               'hidden': True
#           },
#           "fields": "title",
#       }
#   })


def delete_sheet(service, spreadsheet_id, sheet_id):
  """Deletes a sheet."""
  return batch(service, spreadsheet_id, {
      "deleteSheet": {
          "sheetId": sheet_id
      }
  }
  )


def get_sheets(service, spreadsheet_id):
  """Returns all sheets in a spreadsheet."""
  sheet_metadata = service.spreadsheets().get(
      spreadsheetId=spreadsheet_id).execute()
  return sheet_metadata.get('sheets', '')


def cleanup_sheet(service, spreadsheet_id):
  """Cleans up the sheet, removing all sheets except for the first one."""
  sheets = get_sheets(service, spreadsheet_id)
  for sheet in sheets:
    title = sheet.get("properties", {}).get("title")
    sheet_id = sheet.get("properties", {}).get("sheetId")
    if sheet_id == 0 and len(sheets) == 1:
      os.remove("cache/SHEETCACHE")
      rr_print_utils.print_error(
          "Your sheet is empty. Next time you launch me, I will start from the beginning. " +
          DOCS_URI + spreadsheet_id)
    if "jobs" in title and title != "jobs":
      rename_sheet(service, spreadsheet_id, sheet_id, "jobs")
      title = "jobs"
    elif "globals" in title and title != "globals":
      rename_sheet(service, spreadsheet_id, sheet_id, "globals")
      title = "globals"
    elif len(sheets) == 1:
      os.remove("cache/SHEETCACHE")
      rr_print_utils.print_error(
          "Something went terribly wrong. I will create a new sheet if you launch me again.")
    elif title not in ('jobs', 'globals'):
      delete_sheet(service, spreadsheet_id, sheet_id)


def read_from_sheetcache(sheet_name: str) -> str:
  """Reads the sheet cache, checks if the sheet name is correct and returns the ID."""
  with open("cache/SHEETCACHE", "r", encoding="UTF-8") as sheetcache:
    sheetcache_content = sheetcache.read()
  if sheetcache_content.split(";")[0] != sheet_name:
    os.remove("cache/SHEETCACHE")
    rr_print_utils.print_info(
        "You changed the name of the sheet. Authentication is required again.")
    raise FileNotFoundError
  spreadsheet_id = sheetcache_content.split(";")[1]
  rr_print_utils.print_info(f"I'm using this cached spreadsheet: {DOCS_URI + spreadsheet_id}")
  return spreadsheet_id


def sheet_setup_process(sheet_name: str = SHEETNAME) -> str:
  """Full process to setup the access as well as the sheet in the users google drive."""
  authenticated_access = get_authenticated_service()
  try:
    read_from_sheetcache(sheet_name)
  except FileNotFoundError:
    spreadsheet_id = create_sheet(authenticated_access, sheet_name)
    # Open the template sheet in the browser. Not the newly created one!
    webbrowser.open(
        DOCS_URI + TEMPLATE_SHEET_ID)
    with open("cache/SHEETCACHE", "x", encoding="UTF-8") as sheetcache:
      sheetcache.write(sheet_name + ";" + spreadsheet_id)
    rr_print_utils.print_info_input(
        "I Created a new Render Rob Spreadsheet. Please copy both 'jobs' and 'globals"
        "sheet from the template to the newly created document. If you copied them you can close"
        "the tab and")
    for _ in range(7):
      sheets = get_sheets(authenticated_access, spreadsheet_id)
      jobs_c = 0
      globals_c = 0
      for sheet in sheets:
        if "jobs" in sheet.get("properties", {}).get("title"):
          jobs_c += 1
          if jobs_c > 1:
            delete_sheet(authenticated_access, spreadsheet_id,
                         sheet.get("properties", {}).get("sheetId"))
            jobs_c = jobs_c - 1
        if "globals" in sheet.get("properties", {}).get("title"):
          globals_c += 1
          if globals_c > 1:
            delete_sheet(authenticated_access, spreadsheet_id,
                         sheet.get("properties", {}).get("sheetId"))
            globals_c = globals_c - 1
      if jobs_c != 1 or globals_c != 1:
        rr_print_utils.print_warning(
            f"I'm sorry, but you did not copy both sheets to the new spreadsheet. "
            f"Please try again! If you want to see the sheet, it's here: "
            f"{DOCS_URI + spreadsheet_id}")
      else:
        break

    else:
      rr_print_utils.print_error(
          "To be honest, we were never supposed to land here. Please try Running Render Rob again!")
      return None
    cleanup_sheet(authenticated_access, spreadsheet_id)
    webbrowser.open(DOCS_URI + spreadsheet_id)
    rr_print_utils.print_info_input(
        "I opened the spreadsheet and I'll let you fill it out. If you're done")
  return spreadsheet_id


def get_values(service, spreadsheet_id, value_range):
  """Gets values from a spreadsheet."""
  for _ in range(2):
    try:
      result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                   majorDimension="ROWS",
                                                   range=value_range).execute()
    except HttpError as http_error:
      if "Unable to parse range" in http_error.reason:
        cleanup_sheet(service, spreadsheet_id)
      if "not found" in http_error.reason:
        os.remove("cache/SHEETCACHE")
        rr_print_utils.print_error(
            "I couldn't find the sheet. Are you sure you didn't delete it?")
    else:
      break
  else:
    print("Please check your sheet, if it contains a globals and a jobs sheet: " +
          DOCS_URI + spreadsheet_id)
    sys.exit()

  values = result.get('values', [])
  return values


def query_sheet(spreadsheet_id: str) -> Tuple[List[List[str]], List[List[str]]]:
  """Queries the sheet for jobs and globals."""
  authenticated_access = get_authenticated_service()
  jobs_values = get_values(authenticated_access, spreadsheet_id, "jobs!A1:V81")
  globals_values = get_values(authenticated_access, spreadsheet_id, "globals!A1:C7")
  return jobs_values, globals_values
