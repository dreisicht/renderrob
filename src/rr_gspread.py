import gspread
import os
import glob
from oauth2client.service_account import ServiceAccountCredentials

def query_sheet():
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly',
             'https://www.googleapis.com/auth/drive']

    os.chdir('key/')
    mykey = glob.glob("*.json")

    creds = ServiceAccountCredentials.from_json_keyfile_name(mykey[0], scope)
    client = gspread.authorize(creds)

    sheet = client.open('Render Rob')
    ws1 = sheet.get_worksheet(0).get_all_values()
    ws2 = sheet.get_worksheet(1).get_all_values()
    
    # print(ws1)
    
    return ws1, ws2

def login():
    '''
    Function logs into gspread api
    '''
    pass
    # return sheet

def write_data_in_sheet(renderfolder, status, job_nr):
    '''
    Function writes data into gspread
    '''
    login()
    pass