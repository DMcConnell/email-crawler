import os
import base64

import webbrowser
import tempfile
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up the Gmail API connection
def setup_gmail_api():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = Credentials.from_authorized_user_file('token.pickle')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.readonly'])
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            token.write(creds.to_json().encode())

    return build('gmail', 'v1', credentials=creds)

# Get the first email in your inbox
def query_email_snippets(service, query = '', max_results=1):
    try:
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
        else:
            for message in messages:
                msg_id = message['id']
                message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

                payload = message['payload']
                headers = payload['headers']
                snippet = message['snippet']

                subject = ''
                sender = ''
                message_id = ''

                for header in headers:
                    if header['name'] == 'Subject':
                        subject = header['value']
                    if header['name'] == 'From':
                        sender = header['value']
                    if header['name'] == 'Message-ID':
                        message_id = header['value']

                print(f"Message ID: {message_id}")
                print(f"Subject: {subject}")
                print(f"Sender: {sender}")
                print(f"Snippet: {snippet}")
                print("\n\n")

            #    return (subject, sender, snippet)

                data = ''
                if 'parts' in payload:
                    parts = payload['parts']
                    for part in parts:
                        if part['mimeType'] == 'text/plain':
                            data = part['body']['data']
                        elif part['mimeType'] == 'text/html':
                            data = part['body']['data']
                else:
                    data = payload['body']['data']

                text = base64.urlsafe_b64decode(data).decode()

                filepath = 'email-documents/' + message_id + '.html'

                with open(filepath, 'w') as f:
                    file_name = f.name
                    f.write(text)

                    # Open the temporary file in the default web browser
                    # webbrowser.open('file://' + os.path.realpath(file_name))

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    service = setup_gmail_api()
    query_email_snippets(service, query='receipt')
