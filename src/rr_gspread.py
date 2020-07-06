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
from google.oauth2 import service_account
from apiclient import errors


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


# def get_sheet_name():
#     current_path = os.path.dirname(
#         os.path.realpath(__file__)).replace("\\", "/")+"/"
#     try:
#         f_ini = open(current_path + "user/sheetname.ini", "r")
#         sheetname = f_ini.read()
#         f_ini.close()
#     except FileNotFoundError:
#         sheetname = SHEETNAME


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


def get_authenticated_service_drive():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, (['https://www.googleapis.com/auth/drive.file']))

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

    return build('drive', 'v3', credentials=creds)


def get_service_account_service():
    secret_file = os.path.join(os.getcwd(), 'src/service_account.json')
    creds = service_account.Credentials.from_service_account_file(
        secret_file, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)


def get_service_account_service_drive():
    secret_file = os.path.join(os.getcwd(), 'src/service_account.json')
    creds = service_account.Credentials.from_service_account_file(
        secret_file, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)


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
        "https://docs.google.com/spreadsheets/d/" + TEMPLATE_ID)
    webbrowser.open(
        "https://docs.google.com/spreadsheets/d/" + spreadsheet.get('spreadsheetId'))
    return spreadsheet.get('spreadsheetId')


def copy_sheet(service, sa_service):
    template_id = "1prG29lIic0Qqc_fGq5sLdnDh1u8Nkd45MxdaCuRp1Rw"
    new_spreadsheet_id = create_sheet(service)

    dest_body = {
        'destination_spreadsheet_id': new_spreadsheet_id,
    }

    jobs_sheet = sa_service.spreadsheets().sheets().copyTo(
        spreadsheetId=template_id, sheetId=259211185, body=dest_body).execute()
    jobs_sheet_id = jobs_sheet.get("sheetId")
    renameSheet(service, new_spreadsheet_id, jobs_sheet_id, "jobs")

    globals_sheet = sa_service.spreadsheets().sheets().copyTo(
        spreadsheetId=template_id, sheetId=209628393, body=dest_body).execute()
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
    service_sheets = get_authenticated_service()

    try:
        sheetcache = open("src/util/sheetcache", "r")
        spreadsheetId = sheetcache.read()
        sheetcache.close()
    except FileNotFoundError:
        service = get_authenticated_service()
        spreadsheetId = create_sheet(service)
        sheetcache = open("src/util/sheetcache", "x")
        sheetcache.write(spreadsheetId)
        sheetcache.close()
        print_info(
            "Created the Render Rob Spreadsheet. Please copy both sheets from the template sheet to the newly created one.")
        sys.exit()

    jobs_values = get_values(service_sheets, spreadsheetId, "jobs!A1:V81")
    globals_values = get_values(service_sheets, spreadsheetId, "globals!A1:C7")
    return jobs_values, globals_values


def query_files():
    service_drive = get_authenticated_service_drive()
    results = service_drive.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))


def print_permission(service, file_id, permission_id):
    """Print information about the specified permission.

    Args:
      service: Drive API service instance.
      file_id: ID of the file to print permission for.
      permission_id: ID of the permission to print.
    """
    try:
        permission = service.permissions().get(
            fileId=file_id, permissionId=permission_id).execute()

        print(permission)
        # print('Role: %s' % permission['role'])
        for additional_role in permission.get('additionalRole', []):
            print('Additional role: %s' % additional_role)
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def read_as_service_account():
    # sh_service = get_authenticated_service()
    dr_service = get_authenticated_service_drive()
    sa_service = get_service_account_service_drive()
    # newid = create_sheet(sa_service)
    # copy_sheet(sh_service, sa_service)
    id1 = "1prG29lIic0Qqc_fGq5sLdnDh1u8Nkd45MxdaCuRp1Rw"
    id2 = "1_wxJIgni2Ee45WUZNE1XeqzchVRXmYXAwDPOxofIrIs"
    # oa_newsheet_id = "1Qmpo6fB9IufZN_0Py5QiX-hTDNLI4_6TRWJJsdKIYng"
    # sa_newsheet_id = create_sheet(sa_service)
    
    # print(get_values(sa_service, id, "A1:Z8"))
    # dest_body = {
    #     'destination_spreadsheet_id': sa_newsheet_id
    # }

    # jobs_sheet = sa_service.spreadsheets().sheets().copyTo(
    #     spreadsheetId=id, sheetId=259211185, body=dest_body).execute()

    # copy_file(sa_service, id, "Render Rob successfull copy")
    sa_service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # print_permission(sa_service, id1, "owners")
    print_permission(sa_service, id2, "owners")
    # print_permission(sa_service, id1, "")
    print_permission(sa_service, id2, "")
    # print_permission(dr_service, id1, "")
    print_permission(dr_service, id2, "")
    # sa_service.permissions().inert()


def copy_file(service, origin_file_id, copy_title):
    copied_file = {'title': copy_title}
    return service.files().copy(fileId=origin_file_id, body=copied_file).execute()


if __name__ == "__main__":
    # print(os.getcwd())
    print(query_sheet())
    # read_as_service_account()
    # query_files()
