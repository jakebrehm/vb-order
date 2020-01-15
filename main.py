# -*- coding: utf-8 -*-

'''
Creates a summary of Village Burger orders for ease of ordering.
'''

import smtplib
from collections import namedtuple
from configparser import ConfigParser
from datetime import datetime

import gspread
import twilio
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client

# Define script constants
FORM_START = 5

# Connect to the Google Spreadsheets client
scope = [
	'https://spreadsheets.google.com/feeds',
	'https://www.googleapis.com/auth/drive',
]
path = r'credentials.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
client = gspread.authorize(credentials)

# Get a handle to the relevant worksheets
order_sheet = client.open('Village Burger').worksheet('Order')
info_sheet = client.open('Village Burger').worksheet('Info')

# Gather all of the information that was entered on the form
form = {
	'names': order_sheet.col_values(3)[(FORM_START-1):],
	'orders': order_sheet.col_values(4)[(FORM_START-1):],
	'cooks': order_sheet.col_values(5)[(FORM_START-1):],
	'notes': order_sheet.col_values(6)[(FORM_START-1):],
	'payments': order_sheet.col_values(7)[(FORM_START-1):],
}

# Iterate through each data list
for key, value in form.items():
	# Trim each data list to the same length as the names list
	form[key] = value[:11]
	# Add blank strings if necessary to each data list if necessary
	while len(form[key]) < len(form['names']):
		form[key].append('')

# Construct a list of tuples which contain individual order information
all_orders = list(zip(*form.values()))
# Filter blank rows/tuples out of the list
filtered = [order for order in all_orders if any(item for item in order)]
# Recast the tuples as named tuples
order_tuple = namedtuple('Order', ['name', 'order', 'cook', 'notes', 'payment'])
all_orders = [order_tuple(*order) for order in filtered]

# Create a dictionary of all orders, with subdictionaries for counts and notes
orders = {}
for order in all_orders:
	# Handle blank payment methods and initialize the subdictionary
	payment_method = order.payment if order.payment else 'Unspecified'
	if order.payment not in orders:
		orders[payment_method] = {}
	# Construct the full order information, which also includes the cook
	full_order = f'{order.order}: {order.cook}' if order.cook else order.order
	# Increment the order's count or initialize it if necessary
	if full_order in orders[payment_method]:
		orders[payment_method][full_order]['count'] += 1
	else:
		orders[payment_method][full_order] = {'notes': []}
		orders[payment_method][full_order]['count'] = 1
	# Add the notes if necessary
	if order.notes:
		note = f'[{order.name}] {order.notes}'
		orders[payment_method][full_order]['notes'].append(note)

# Create the subject
subject = f"Village Burger Order ({datetime.today().strftime(r'%m-%d-%Y')})"

# Create the message
total_orders = len(all_orders)
credit_orders = sum(1 for order in all_orders if order.payment == 'Credit')
cash_orders = sum(1 for order in all_orders if order.payment == 'Cash')
unspecified_orders = sum(1 for order in all_orders if order.payment == '')
# Construct the message introduction
message = (
	f'From a total of {total_orders} order(s), {credit_orders} will '
	f'be paid with credit, {cash_orders} will be paid with cash, and '
	f'{unspecified_orders} did not specify a payment method.\n\n'
)
# Create sections for each payment method
methods = []
if credit_orders: methods.append('Credit')
if cash_orders: methods.append('Cash')
if unspecified_orders: methods.append('Unspecified')
for m, method in enumerate(methods):
	# Add a title for the payment method
	message += f'{method.upper()}:\n'
	# Iterate through the orders for the given payment method and add them
	for order_name, order_info in orders[method].items():
		message += f"({order_info['count']}) {order_name}\n"
		# Add the notes if any exist
		if order_info['notes']:
			for note in order_info['notes']:
				message += f"\t{note}\n"
	# Add a new line to all sections but the last
	if m < (len(methods) - 1): message += '\n'

# Instantiate the ConfigParser
parser = ConfigParser()
parser.read(r'config.ini')

# Gather all email addresses from the spreadsheet where the box is checked
emails = [email for e, email in enumerate(info_sheet.col_values(3)[3:], start=4)
				if email and info_sheet.acell(f'D{e}').value == 'TRUE']
# Initialize the STMP server
username = parser['login']['username']
password = parser['login']['password']
with smtplib.SMTP('smtp.gmail.com', 587) as server:
	server.ehlo()
	server.starttls()
	server.login(username, password)
	# Construct and send the email to all recipients
	email = f'Subject: {subject}\n\n{message}'
	for address in emails:
		server.sendmail(username, address, email.encode('utf-8'))

# Gather all phone number from the spreadsheet where the box is checked
phones = [phone for p, phone in enumerate(info_sheet.col_values(5)[3:], start=4)
				if phone and info_sheet.acell(f'F{p}').value == 'TRUE']
# Initialize the Twilio client
number = parser['twilio']['number']
accountSID = parser['twilio']['sid']
authToken = parser['twilio']['token']
twilio_client = Client(accountSID, authToken)
# Send a text message summary to all recipients
for phone in phones:
	try:
		twilio_client.messages.create(body=message, from_=number, to=phone)
	except twilio.base.exceptions.TwilioRestException:
		print(f'An error occurred when attempting to send a text to {phone}.')

# Show on the spreadsheet that the order is in
order_sheet.update_acell('F26', 'Submitted')