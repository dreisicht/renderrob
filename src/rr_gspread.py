import gspread
import os
import glob
import configparser
from oauth2client.service_account import ServiceAccountCredentials


def query_sheet():
    scope = ['https://www.googleapis.com/auth/spreadsheets.readonly',
             'https://www.googleapis.com/auth/drive']

    os.chdir('key/')
    jsonfiles = glob.glob("*.json")

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        jsonfiles[0], scope)
    client = gspread.authorize(creds)
    current_path = os.path.dirname(
        os.path.realpath(__file__)).replace("\\", "/")+"/"
    try:
        f_ini = open(current_path + "util/sheetname.ini", "r")
        sheetname = f_ini.read()
        f_ini.close()
    except FileNotFoundError:
        sheetname = 'Render Rob'
    sheet = client.open(sheetname)
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


if __name__ == "__main__":
    print(query_sheet())
