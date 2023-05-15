""" This module contains functions to interact with Google Sheets API."""
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from util import rr_printing

SHEETNAME = 'Render Rob 2.0'
TEMPLATE_SHEET_ID = "1prG29lIic0Qqc_fGq5sLdnDh1u8Nkd45MxdaCuRp1Rw"
DOCS_URI = "https://docs.google.com/spreadsheets/d/"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_PATH = "cache/token.pickle"


def get_credentials_path() -> str:
  """Returns the credentials path."""
  for filename in os.listdir("cache/"):
    if filename.endswith(".json"):
      return "cache/" + filename


def authorize_user() -> any:
  """Authorizes the user and returns the credentials."""
  creds = None

  if os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH, "rb") as token_file:
      creds = pickle.load(token_file)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          get_credentials_path(), scopes=SCOPES
      )
      creds = flow.run_local_server(port=0)
    with open(TOKEN_PATH, "wb") as token_file:
      pickle.dump(creds, token_file)

  return creds


def get_user_name(service) -> str:
  """Returns the user name."""
  about = service.about().get(fields='user').execute()
  user = about.get('user', {})
  return user.get('displayName', '').split(" ")[0]


def rename_file(service, file_id, new_name) -> None:
  """Renames the file."""
  service.files().update(fileId=file_id, body={'name': new_name}).execute()


def copy_spreadsheet(service, spreadsheet_id):
  """Copies the spreadsheet and returns the ID."""
  copy_body = {
      'name': 'Copy of Public Spreadsheet'
  }
  request = service.files().copy(fileId=spreadsheet_id, body=copy_body)
  response = request.execute()
  return response['id']


def read_spreadsheet(service, spreadsheet_id, value_range):
  """Reads the spreadsheet and returns the values."""
  result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                               majorDimension="ROWS",
                                               range=value_range).execute()
  values = result.get('values', [])
  if not values:
    rr_printing.print_error('No data found.')
  else:
    return values


def get_spreadsheet_id_or_create(drive_service: any) -> str:
  """Reads the sheet cache, checks if the sheet name is correct and returns the ID."""
  if not os.path.exists("cache/SHEETCACHE"):
    rr_printing.print_info("No sheet cache found. Creating a new one.")
    spreadsheet_id = copy_spreadsheet(drive_service, TEMPLATE_SHEET_ID)
    rename_file(drive_service, spreadsheet_id, SHEETNAME + " " + get_user_name(drive_service))
    with open("cache/SHEETCACHE", "w", encoding="UTF-8") as sheetcache:
      sheetcache.write(spreadsheet_id)
  else:
    with open("cache/SHEETCACHE", "r", encoding="UTF-8") as sheetcache:
      spreadsheet_id = sheetcache.read()
    rr_printing.print_info(f"I'm using this cached spreadsheet: {DOCS_URI + spreadsheet_id}")

  return spreadsheet_id


def download_spreadsheet_content():
  """Downloads the spreadsheet content and returns the values."""
  creds = authorize_user()
  drive_service = build('drive', 'v3', credentials=creds)
  rr_printing.print_info(f"Hello {get_user_name(drive_service)}!")
  spreadsheet_id = get_spreadsheet_id_or_create(drive_service)
  spreadsheet_service = build("sheets", "v4", credentials=creds)
  jobs_values = read_spreadsheet(spreadsheet_service, spreadsheet_id, "jobs!A1:V81")
  globals_values = read_spreadsheet(spreadsheet_service, spreadsheet_id, "globals!A1:C7")
  return jobs_values, globals_values


if __name__ == "__main__":
  print(download_spreadsheet_content())
