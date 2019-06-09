import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Connect to the Google Spreadsheets client
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
path = 'credentials.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
client = gspread.authorize(creds)

# Specify the active worksheet
sheet = client.open("Village Burger").worksheet('Info')

first = sheet.acell('C4').value
second = sheet.acell('D4').value

print(first)
print(second)
print(second == 'TRUE')

# emails = sheet.col_values(3)[3:]
# emails = [email for email in sheet.col_values(3) if sheet.acell().value == 'TRUE']
# emails = []
# for e, email in enumerate(sheet.col_values(3)[3:], start=4):
# 	print(f'D{e}')

# 	if sheet.acell(f'D{e}').value == 'TRUE':
# 		emails.append(email)




emails = [email for e, email in enumerate(sheet.col_values(3)[3:], start=4)
	if sheet.acell(f'D{e}').value == 'TRUE']

print(emails)

