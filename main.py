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
names = [name for name in sheet.col_values(3)[4:26] if name.lower() != 'order in']
orders = sheet.col_values(4)[4:26]
cooks = sheet.col_values(5)[4:26]
notes = sheet.col_values(6)[4:26]
payments = sheet.col_values(7)[4:26]

# Initialize information of the orders
info = {}
for order in set(orders):
	info[order] = {
		'count': orders.count(order),
		'cash': sum(1 for p, payment in enumerate(payments) if orders[p] == order
					and payment == 'Cash'),
		'credit': sum(1 for p, payment in enumerate(payments) if orders[p] == order
					and payment == 'Credit'),
		'notes': '',
		}

# Record the cook(s) for each order
for order in set(orders):
	info[order]['cook'] = [cook for c, cook in enumerate(cooks) if orders[c] == order]

# Create a new line for each note
for n, note in enumerate(notes):
	if note: info[orders[n]]['notes'] += f'({names[n]}) {note}\n'

# Create the message of the email
message = f'There are {len(names)} people going to Village Burger today.\n'
message += f'Of those {len(names)} people, {payments.count("Credit")} are ' \
		   f'paying with credit and {payments.count("Cash")} are paying with ' \
		    'cash.\n\n'

for i, order in enumerate(info.keys()):
	# Specify order number and what the order is
	message += f'ORDER #{i+1}:\n'
	message += f'({info[order]["count"]}) {order}\n'
	# Specify the cook(s) of the order(s)
	cook_string = ''
	for cook in set(info[order]['cook']):
		if cook: cook_string += f'({info[order]["cook"].count(cook)}) {cook} '
	if cook: message += cook_string + '\n'
	# Add payment information and notes
	message += f'({info[order]["credit"]}) Credit ({info[order]["cash"]}) Cash\n'
	message += f'{info[order]["notes"]}'
	message += '\n'

# Create the subject of the email
date = datetime.today().strftime('%m/%d/%Y')
subject = f'Village Burger Order ({date})'

# Read username and password from the config file
parser = ConfigParser()
parser.read('config.ini')
username = parser['login']['username']
password = parser['login']['password']

# Define the recipients of the email
recipients = ['Jake', 'Jake 2']
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