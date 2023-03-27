"""
Script for sending emails from `tablinks.csv` (retrieved via `export_tablinks.py`)
"""

import smtplib
import ssl
import time
import pandas as pd
from getpass import getpass
from email_tools import create_email

# SMTP settings
USER = 'josef@hoppe.io'
SENDER_ADDRESS = 'tabgoettingen@hoppe.io'
SMTP_ADDRESS = 'ssl0.ovh.net'
SMTP_PORT = 465
password = getpass("Type your password and press enter: ")
# delay in seconds to avoid being classified as SPAM
EMAIL_DELAY = 60

# email content settings
TABMASTER_FULL = 'Josef Hoppe'
TABMASTER_GREETING = 'Josef'
TOURNAMENT_NAME = 'CD Goettingen'

# load data
df_tablinks = pd.read_csv('tablinks.csv', index_col='debaterHref')
print(f'loaded {len(df_tablinks)} debaters for sending emails.')

# Create a secure SSL context
context = ssl.create_default_context()

for idx, row in df_tablinks.iterrows():
    with smtplib.SMTP_SSL(SMTP_ADDRESS, SMTP_PORT, context=context) as server:
        print(server.login(USER, password))
        to_addr = row['email']
        first_name = row['firstName']
        tablink = row['registrationLink']
        print(f'[{idx}] sending to {row["name"]} ({to_addr})')
        message = create_email(SENDER_ADDRESS, TABMASTER_FULL,
                               TABMASTER_GREETING, to_addr, first_name, tablink, TOURNAMENT_NAME)
        print(f'[{idx}] send result: ', server.sendmail(SENDER_ADDRESS, to_addr,
              message.as_string().encode('utf-8')))
        time.sleep(EMAIL_DELAY)
        server.close()
