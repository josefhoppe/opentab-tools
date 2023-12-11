"""
Script for sending emails from `tablinks.csv` (retrieved via `export_tablinks.py`)
"""

import smtplib
import ssl
import time
import os.path
import pandas as pd
from getpass import getpass
from email_tools import create_email

def fb_link(tablink: str) -> str:
    """
    Transforms the tablink to the final feedback link
    (Tablink contains useful secret)
    """
    token = tablink.split('/')[-1]
    if token == '':
        token = tablink.split('/')[-2] #Tabbycat
    return f'https://feedback.hoppe.io/[tournament]/{token}.html'


def check_send(tablink: str) -> bool:
    """
    Checks whether to send the email (only if feedback exists in local directory)
    """
    token = tablink.split('/')[-1]
    if token == '':
        token = tablink.split('/')[-2] #Tabbycat
    fb_file = f'feedback/{token}.html'
    return os.path.exists(fb_file)

# SMTP settings
USER = 'josef@hoppe.io'
SENDER_ADDRESS = '[tournament]@hoppe.io'
SMTP_ADDRESS = 'ssl0.ovh.net'
SMTP_PORT = 465
password = getpass("Type your password and press enter: ")
# delay in seconds to avoid being classified as SPAM
EMAIL_DELAY = 30

# email content settings
TABMASTER_FULL = 'Josef Hoppe'
TABMASTER_GREETING = 'Josef'
TOURNAMENT_NAME = '[Tournament]'

# load data
if os.path.exists('tablinks.csv'):
    # OpenTab
    df_tablinks = pd.read_csv('tablinks.csv', index_col='debaterHref')
elif os.path.exists('tablinks_tc.csv'):
    # TabbyCat
    df_tablinks = pd.read_csv('tablinks_tc.csv', sep='\t')
    df_tablinks.set_index('name', drop=False, inplace=True)
    df_emails = pd.read_csv('emails_tc.csv', sep='\t', index_col=0).loc[:,['email']]
    df_tablinks = df_tablinks.join(df_emails)

print(f'loaded {len(df_tablinks)} debaters for sending emails.')

# Create a secure SSL context
context = ssl.create_default_context()

for idx, row in df_tablinks.iterrows():
    tablink = row['registrationLink'] if 'registrationlink' in row else row['url']
    if check_send(tablink):
        with smtplib.SMTP_SSL(SMTP_ADDRESS, SMTP_PORT, context=context) as server:
            print(server.login(USER, password))
            to_addr = row['email']
            first_name = row['firstName'] if 'firstName' in row else row['name']
            print(f'[{idx}] sending to {row["name"]} ({to_addr})')
            message = create_email(SENDER_ADDRESS, TABMASTER_FULL,
                                TABMASTER_GREETING, to_addr, first_name, fb_link(tablink), TOURNAMENT_NAME, 'feedback')
            print(f'[{idx}] send result: ', server.sendmail(SENDER_ADDRESS, to_addr,
                message.as_string().encode('utf-8')))
            time.sleep(EMAIL_DELAY)
            server.close()
