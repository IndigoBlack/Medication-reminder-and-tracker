from google.auth.transport.requests import Request
from google.oauth2 import InstalledAppFlow
from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import questionary
import requests
import datetime
import csv
import os

# Medication scheduling. Mabe use google calender for this
# Track Whether the user has taken their medicine

SCOPE = ["https://www.googleapis.com/auth/calendar"]

def main():
    ...

def authorise():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorised_user_file("token.json", SCOPE)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPE)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print("An error occured:", error)
        return None

def schedule(service, summary, description, start_date, end_date):
    # Use google calendar to shedule a reminder
    event = {
        "summary": summary, # The summary should indicate which medication to take 
        "description": description, # description should indicate how the medication should be taken
        "start": {
            "dateTime": start_date,
            "timezone": "Africa/Johannesburg"
        },
        "end": {
            "dateTime": end_date,
            "timezone": "Africa/Johannesburg"
        },
        "reminder": {
            "userDefault": False,
            "overrides": [
                {"method": "email", "minutes": 60},
                {"method": "popup", "minutes": 60}
            ],
        },
    }
    try:
        reminder = service.events().insert(calendarId="primary", body=event).execute()
        print(f"Reminder created: {reminder.get("htmlLink")}")
        return reminder
    except HttpError as error:
        print("An error occured:", error)

# Track whether the medication has been taken: Self-reporting is a good option.
def self_track(pills):
    times = ["00:00", "02:00", "03:00", 
             "04:00", "05:00", "06:00", 
             "07:00", "08:00", "09:00", 
             "10:00", "11:00", 
             "12:00", "13:00", "14:00", 
             "15:00", "16:00", "17:00", 
             "18:00", "19:00", "20:00", 
             "21:00", "22:00", "23:00"]
    date = questionary.select("Around which hour did you take your medicine", choices=times)
    
    with open("track.csv", "a") as file:
        writer = csv.writer(file)

        writer.writerow(["Date", "Hour", "How many taken"])

        writer.writerow([datetime.date.today(), date, pills])
    
    return "Psuedo-tracked"

# Indicate whether the medication and needs a refill, if it does set a refill date
# Option:
#   if possible use google maps API to show pharmacies that are close that the patient can get a refill at
#   Call an api that will give you information about the medication when requested:
#       Search up the which API to use for this

url = "https://api.fda.gov/drug/label.json"

params = {
    "search": "aspirin",
    "limit": 1
}
response = requests.get(url, params=params)
data = response.json()

for result in data.get("results"):
    print(result.get("description", ""))