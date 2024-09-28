import gspread
from decouple import config
import json
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

class connection_google_sheets():

    def __init__(self):
        scope = ['https://www.googleapis.com/auth/spreadsheets', 
            'https://www.googleapis.com/auth/drive']
        credentials =  ServiceAccountCredentials.from_json_keyfile_dict(json.loads(config('ACCOUNT_SERVICE_SHEET')), scope)
        self.client = gspread.authorize(credentials)

    def get_list_file(self):
        return self.client.openall()
    
    def read_file(self, id):
        return self.client.open_by_key(id)

    def get_all_sheets(self, file):
        return file.worksheets()
    
    def sheet_to_df(self, file, sheet_name):
        worksheet = file.worksheet(sheet_name)
        data = worksheet.get_all_values()
        return pd.DataFrame(data[2:], columns=data[1])

    def delete_file(self, id):
        self.client.del_spreadsheet(id)