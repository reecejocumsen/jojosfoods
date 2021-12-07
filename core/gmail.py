"""This file uses functions sourced from two online tutorials
    https://www.thepythoncode.com/article/use-gmail-api-in-python
    https://mailtrap.io/blog/send-emails-with-gmail-api/

    Both of these were first accessed on the 23rd of September
"""

from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
from email.mime.text import MIMEText
from base64 import urlsafe_b64decode, urlsafe_b64encode

SCOPES = ['https://mail.google.com/']
our_email = 'contactjojosfodos@gmail.com'

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    service = gmail_authenticate()
    message = create_message('contactjojosfoods@gmail.com', 'alexpatapan@gmail.com', 'testing', 'testing text')
    send_message(service, message)

# Function taken from https://mailtrap.io/blog/send-emails-with-gmail-api/
def send_message(service, message, user_id='contactjojosfoods@gmail.com'):
  try:
    message = service.users().messages().send(userId=user_id, body=message).execute()
    print('Message Id: %s' % message['id'])
    return message
  except Exception as e:
    print('An error occurred: %s' % e)
    return None

# Function taken from https://www.thepythoncode.com/article/use-gmail-api-in-python
def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# Function taken from https://mailtrap.io/blog/send-emails-with-gmail-api/
def create_message(sender, to, subject, message_text):
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  raw_message = urlsafe_b64encode(message.as_string().encode("utf-8"))
  return {
    'raw': raw_message.decode("utf-8")
  }

if __name__ == '__main__':
    main()