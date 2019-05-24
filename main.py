import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from datetime import datetime

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

sheet = client.open("Village Burger").sheet1

names = [name for name in sheet.col_values(3)[4:26] if name.lower() != 'order in']
orders = sheet.col_values(4)[4:26]
cooks = sheet.col_values(5)[4:26]
notes = sheet.col_values(6)[4:26]
payments = sheet.col_values(7)[4:26]

info = {}
for order in set(orders):
	info[order] = {
		'count': orders.count(order),
		'cash': sum(1 for p, payment in enumerate(payments) if orders[p] == order and payment == 'Cash'),
		'credit': sum(1 for p, payment in enumerate(payments) if orders[p] == order and payment == 'Credit'),
		'notes': '',
		}

for order in set(orders):
	info[order]['cook'] = [cook for c, cook in enumerate(cooks) if orders[c] == order]


for n, note in enumerate(notes):
	if note: info[orders[n]]['notes'] += f'({names[n]}) {note}\n'

message = f'There are {len(names)} people going to Village Burger today.\n'
message += f'Of those {len(names)} people, {payments.count("Credit")} are paying with credit and {payments.count("Cash")} are paying with cash.\n'
message += '\n'

for i, order in enumerate(info.keys()):
	message += f'ORDER #{i+1}:\n'
	message += f'({info[order]["count"]}) {order}\n'
	message += f'({info[order]["credit"]}) Credit ({info[order]["cash"]}) Cash\n'

	cook_string = ''
	for cook in set(info[order]['cook']):
		if cook: cook_string += f'({info[order]["cook"].count(cook)}) {cook} '
	if cook: message += cook_string + '\n'

	message += f'{info[order]["notes"]}'
	message += '\n'

# Either email or text this message
print(message)

date = datetime.today().strftime('%m/%d/%Y')

subject = f'Village Burger Order ({date})'

sender = 'thegingler@gmail.com'
password = 'ginglebells'

server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()
server.login(sender, password)

recipients = {
	1: {'first': 'Gingle', 'last': 'Meister', 'sex':'Beast', 'email': 'thegingler@gmail.com'},
	2: {'first': 'Jacob', 'last': 'Brehm', 'sex':'Male', 'email': 'jake.m.brehm@gmail.com'},
	3: {'first': 'Jacob', 'last': 'Brehm', 'sex':'Male', 'email': 'jbrehm@tactair.com'},
}

email = 'Subject: {}\n\n{}'.format(subject, message)

for i in range(len(recipients)):
	server.sendmail(sender, recipients[i+1]['email'], email)
server.quit()
print('Success!')