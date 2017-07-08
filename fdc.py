#!/usr/bin/env python3

import argparse
import httplib2
import os
import datetime
import re
import dateutil.parser
import time
from pprint import pprint
import smtplib
from email.message import EmailMessage
import pytz

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from ruamel import yaml
import requests


SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if args:
            credentials = tools.run_flow(flow, store, args)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def event_to_string(e):
    s = 'Zusammenfassung: {}\n{} - {}\nBeschreibung: {}\nLink: {}\n\n'.format(
        e['summary'], e['start']['dateTime'], e['end']['dateTime'], e.get('description', '-'),
        e['htmlLink'])
    return s


def mail(text):
    msg = EmailMessage()
    msg.set_content(text)
    # TODO add event and reason to content

    msg['Subject'] = config['mail subject']
    msg['From'] = config['mail from']
    msg['To'] = config['mail to']

    # Send the message via our own SMTP server.
    s = smtplib.SMTP(config['smtp host'])
    s.send_message(msg)
    s.quit()


def main():
    """
    Main rutine with infinite loop checkin calendar
    """
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument('config', type=argparse.FileType('r'), help='YAML config file')
    global args, config
    args = parser.parse_args()
    config = yaml.safe_load(args.config)
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    grace = datetime.timedelta(seconds=config['grace seconds'])
    fail_state = False
    
    while True:
        now_str = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        eventsResult = service.events().list(
            calendarId=config['calendar id'], timeMin=now_str, maxResults=10 , singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        
        # Filter full-day events
        events = [e for e in events if 'dateTime' in e['start']]
        # Filter based on summary regex
        events = [e for e in events if re.match(config['event summary filter'], e['summary'])]
        
        for e in events:
            # Parse dateTime
            e['start']['dateTime'] = dateutil.parser.parse(e['start']['dateTime'])
            e['end']['dateTime'] = dateutil.parser.parse(e['end']['dateTime'])
        
        if not events:
            print('No upcoming events found.')
            return
        else:
            print('Relevant event:')
            print(event_to_string(events[0]))

        now = datetime.datetime.now(pytz.utc)
        open_door_required = (events[0]['start']['dateTime'] + grace < now)
        
        if not open_door_required:
            fail_state = False
            print('Don\'t care (not yet started)')
            sleep = (events[0]['start']['dateTime'] + grace - now).seconds
            print('Sleeping for {}s until {}'.format(sleep, events[0]['start']['dateTime'] + grace))
            time.sleep(sleep)
            continue
        
        open_state = requests.get(config['spaceapi url']).json()['state']['open']
        
        if not open_state:
            if not fail_state:
                print('OH NOES... we suck... (ongoing open time, but door closed)')
                fail_state = True
                mail('{}\n\n{}'.format(config['fail text'], event_to_string(events[0])))
            else:
                print('still failing :(')
            sleep = config['poll seconds']
            print('Sleeping for {}s'.format(sleep))
            time.sleep(sleep)
            continue
        else:
            if fail_state:
                print('Opened just now! :) (ongoing open time and door open)')
                fail_state = False
                mail('{}\n\n{}'.format(config['yay text'], event_to_string(events[0])))
            else:
                print('All good :) (ongoing open time and door open)')
            sleep = config['poll seconds']
            print('Sleeping for {}s'.format(sleep))
            time.sleep(sleep)
            continue


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
