# from __future__ import print_function
import time
from time import sleep
from twilio.rest import Client
import keys
import requests
from bs4 import BeautifulSoup

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
# GET CALENDER EVENT
GOOGLE_KEY = keys.google_key

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=1, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')


    # Prints the start and name of the next 10 events
    start = events[0]['start'].get('dateTime', events[0]['start'].get('date'))
    print(start, events[0]['summary'])

except HttpError as error:
    print('An error occurred: %s' % error)

# CALCULATE AND GET BUS TIME
# STOP SCHEDULE
stop_times_iter = "6:18-6:33-6:49-7:04-7:20-7:36-7:52-8:08-8:24-8:40-8:56-9:12-9:27-9:43-9:59-10:15-10:32-11:08-11:45-12:22-12:59-13:36-14:13-14:29-14:45-15:03-15:19-15:35-15:50-16:06-16:22-16:38-16:54".split('-')
stop_times_TIMES = []
print(stop_times_iter)
for time in stop_times_iter:
    stop_times_TIMES.append(time.split(':'))

stop_times_SECONDS = []
for time in stop_times_TIMES:
    stop_times_SECONDS.append(int(time[0])*3600 + int(time[1])*60)

time_TIME = start[11:16].split(':')

event_time_SECONDS = (int(time_TIME[0])*3600 + int(time_TIME[1])*60)

if event_time_SECONDS == 39600:
    time_to_school = 5400
else:
    time_to_school = 7200

# FIND BEST TIME
index = 0
MESSAGE = "NO BUS FOUND"
print(event_time_SECONDS)
for time in stop_times_SECONDS:
    print("TIME", time)
    if event_time_SECONDS - 600 <= time + time_to_school and time + time_to_school <= event_time_SECONDS + 600:
        if int(stop_times_TIMES[index][0]) < 12:
            end = "a.m."
        else:
            end = "p.m."
        if int(stop_times_TIMES[index][1]) - 10 < 0:
            stop_times_TIMES[index][0] = int(stop_times_TIMES[index][0])-1
            stop_times_TIMES[index][1] = 60 - (10 - int(stop_times_TIMES[index][1]))
        else:
            stop_times_TIMES[index][1] = int(stop_times_TIMES[index][1]) - 10
        MESSAGE = f"LEAVE HOUSE AT: {stop_times_TIMES[index][0]}:{stop_times_TIMES[index][1]} {end}"
        break
    index += 1
print(MESSAGE)
# Send SMS
if MESSAGE != "NO BUS FOUND":
    client = Client(keys.account_sid, keys.auth_token)

    message = client.messages.create(
        body= MESSAGE,
        from_= keys.twilio_number,
        to = keys.target_number
    )
    print(message.body)

