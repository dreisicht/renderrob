import gspread
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

googleAPI = '/pathToSecret.json'
scope = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(googleAPI)
scopedCreds = credentials.with_scopes(scope)
gc = gspread.Client(auth=scopedCreds)
gc.session = AuthorizedSession(scopedCreds)
sheet = gc.open("MyDoc").sheet1
