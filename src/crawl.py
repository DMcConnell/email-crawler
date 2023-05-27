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
from bs4 import BeautifulSoup

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
def query_email_snippets(service, query = '', max_results=1, strip_html=False, base_dir='email-documents'):
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
                text = subject + '\n\n' + sender + '\n\n' + text
                filepath = base_dir + '//' + message_id
               
                if strip_html:
                    text = html_to_text(text)
                    filepath = filepath + '.txt'
                else:
                    filepath = filepath + '.html'

                with open(filepath, 'w') as f:
                    file_name = f.name
                    f.write(text)

                    # Open the temporary file in the default web browser
                    # webbrowser.open('file://' + os.path.realpath(file_name))

    except HttpError as error:
        print(f"An error occurred: {error}")


def html_to_text(html_str):
    html_file = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
    html_file.write(html_str)
    html_file.close()

    filepath = html_file.name

    with open(filepath, 'r') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


if __name__ == '__main__':
    service = setup_gmail_api()

    query_email_snippets(service, max_results=200, strip_html=True, base_dir='email-documents-cleaned')
