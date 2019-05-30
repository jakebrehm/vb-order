import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from datetime import datetime
from configparser import ConfigParser

# Connect to the Google Spreadsheets client
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Specify the active worksheet
sheet = client.open("Village Burger").sheet1

# Pull data from each column of the spreadsheet
names = [name for name in sheet.col_values(3)[4:24] if name.lower() != 'order in']
orders = sheet.col_values(4)[4:24]
cooks = sheet.col_values(5)[4:24]
notes = sheet.col_values(6)[4:24]
payments = sheet.col_values(7)[4:24]

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
cash = {order: {'count': details['count'], 'notes': details['notes']} for order, details in cash.items()
		if details['count'] > 0}

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
credit = {order: {'count': details['count'], 'notes': details['notes']} for order, details in credit.items()
		if details['count'] > 0}

# Create the message of the email
message = f'There were {len(names)} orders entered into the spreadsheet today.\n'
message += f'Of those {len(names)} orders, {payments.count("Credit")} will ' \
		   f'be paid with credit and {payments.count("Cash")} will be paid ' \
		    'with cash.\n\n'

# Create the message of the email
message += 'CASH:\n'
for i, order in enumerate(cash):
	message += f'({cash[order]["count"]}) {order}\n'
	if cash[order]['notes']: message += cash[order]['notes']
message += '\n'
message += 'CREDIT:\n'
for i, order in enumerate(credit):
	message += f'({credit[order]["count"]}) {order}\n'
	if credit[order]['notes']: message += credit[order]['notes']

# Create the subject of the email
date = datetime.today().strftime('%m/%d/%Y')
subject = f'Village Burger Order ({date})'

# Read username and password from the config file
parser = ConfigParser()
parser.read('config.ini')
username = parser['login']['username']
password = parser['login']['password']

# Define the recipients of the email
recipients = ['Jake 2']
recipients = {recipient: parser['recipients'][recipient] for recipient in recipients}

# Start the server and login
server = smtplib.SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.login(username, password)

# Format and send email to all recipients
email = 'Subject: {}\n\n{}'.format(subject, message)
for recipient in recipients:
	server.sendmail(username, recipients[recipient], email.encode('utf-8'))

# Quit the server
server.quit()

# Show on the spreadsheet that order is in
sheet.update_acell('F26', 'Submitted')