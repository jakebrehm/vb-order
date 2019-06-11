import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Connect to the Google Spreadsheets client
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
path = r'C:\Users\brehm\OneDrive\Python\Leisure Projects\Village Burger\credentials.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
client = gspread.authorize(creds)

# Specify the active worksheet
sheet = client.open("Village Burger").sheet1

# Clear all data
cells = sheet.range('C5:G25')
for cell in cells: cell.value = ''
sheet.update_cells(cells)

# Set the order status to pending
sheet.update_acell('F26', 'Pending')

# Clear the burger of the week
sheet.update_acell('D3', '')

sheet.update_acell('D3', '=IMAGE("http://www.villageburgerliverpool.com/buff.jpg", 1)')