import gspread
import smtplib
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client as tc
from configparser import ConfigParser
from lemons.gui import ResourcePath

# Connect to the Google Spreadsheets client
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
path = r"C:\Users\brehm\OneDrive\Python\Leisure Projects\Village Burger\credentials.json"
# path = ResourcePath('credentials.json')
creds = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
client = gspread.authorize(creds)

# Specify the active worksheet
sheet = client.open("Village Burger").sheet1

# Pull data from each column of the spreadsheet
names = [name for name in sheet.col_values(3)[4:24] if name.lower() != 'order in']
orders = sheet.col_values(4)[4:24]
cooks = sheet.col_values(5)[4:24]
notes = sheet.col_values(6)[4:24]
payments = sheet.col_values(7)[4:24]

# Make sure all lists are the same length
for info_list in [names, orders, cooks, notes, payments]:
	while len(info_list) < len(names):
		info_list.append('')

# Create a dictionary to fill with cash orders
cash = {}
for i, order in enumerate(orders):
	cook = f': {cooks[i]}' if cooks[i] else ''
	full = order + cook
	# Count all of the orders with the same name and cook
	cash[full] = {
		'count': sum(1 for p, payment in enumerate(payments) if orders[p] == order
				     and payment == 'Cash' and cooks[i] == cooks[p]),
		'notes': '',
	}
# Add notes to the relevant dictionary
for n, note in enumerate(notes):
	if note and payments[n] == 'Cash':
		cook = f': {cooks[n]}' if cooks[n] else ''
		cash[orders[n] + cook]['notes'] +=  f'\t({names[n]}) {note}\n'
# Remove items with a count of zero from the dictionary
cash = {order: {'count': details['count'], 'notes': details['notes']}
        for order, details in cash.items() if details['count'] > 0}

# Create a dictionary to fill with credit orders
credit = {}
for i, order in enumerate(orders):
	cook = f': {cooks[i]}' if cooks[i] else ''
	full = order + cook
	# Count all of the orders with the same name and cook
	credit[full] = {
		'count': sum(1 for p, payment in enumerate(payments) if orders[p] == order
					 and payment == 'Credit' and cooks[i] == cooks[p]),
		'notes': '',
	}
# Add notes to the relevant dictionary
for n, note in enumerate(notes):
	if note and payments[n] == 'Credit':
		cook = f': {cooks[n]}' if cooks[n] else ''
		credit[orders[n] + cook]['notes'] +=  f'\t({names[n]}) {note}\n'
# Remove items with a count of zero from the dictionary
credit = {order: {'count': details['count'], 'notes': details['notes']}
          for order, details in credit.items() if details['count'] > 0}

# Sort the cash orders alphabetically
cash_sorted = list(cash.keys())
cash_sorted.sort()

# Sort the credit orders alphabetically
credit_sorted = list(credit.keys())
credit_sorted.sort()

# Create the message of the email
message = f'There were {len(names)} orders entered into the spreadsheet today.\n'
message += f'Of those {len(names)} orders, {payments.count("Credit")} will ' \
		   f'be paid with credit and {payments.count("Cash")} will be paid ' \
		    'with cash.\n\n'

# Create the message of the email
message += 'CASH:\n'
for i, order in enumerate(cash_sorted):
	message += f'({cash[order]["count"]}) {order}\n'
	if cash[order]['notes']: message += cash[order]['notes']
message += '\n'
message += 'CREDIT:\n'
for i, order in enumerate(credit_sorted):
	message += f'({credit[order]["count"]}) {order}\n'
	if credit[order]['notes']: message += credit[order]['notes']

# Create the subject of the email
subject = f'Village Burger Order'

# Read username and password from the config file
parser = ConfigParser()
parser.read(r"C:\Users\brehm\OneDrive\Python\Leisure Projects\Village Burger\config.ini")
# parser.read(ResourcePath('config.ini'))
username = parser['login']['username']
password = parser['login']['password']

# Gather the recipients of the email
info_sheet = client.open("Village Burger").worksheet('Info')
emails = [email for e, email in enumerate(info_sheet.col_values(3)[3:], start=4)
	if info_sheet.acell(f'D{e}').value == 'TRUE' and info_sheet.acell(f'C{e}').value]

# Start the server and login
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.login(username, password)

# Format and send email to all recipients
email = 'Subject: {}\n\n{}'.format(subject, message)
for address in emails:
	server.sendmail(username, address, email.encode('utf-8'))

# Quit the server
server.quit()

# Gather the recipients of the texts
numbers = [number for n, number in enumerate(info_sheet.col_values(5)[3:], start=4)
	if info_sheet.acell(f'F{n}').value == 'TRUE' and info_sheet.acell(f'E{n}').value]

twilio_number = parser['twilio']['number']
accountSID = parser['twilio']['sid']
authToken = parser['twilio']['token']
twilio_client = tc(accountSID, authToken)

# Send text to all recipients
for number in numbers:
	twilio_client.messages.create(body=message, from_=twilio_number, to=number)

# Show on the spreadsheet that order is in
sheet.update_acell('F26', 'Submitted')