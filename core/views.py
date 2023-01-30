from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import HttpResponse, HttpResponseRedirect
import requests
from googleapiclient.discovery import build
import os
import json
from django.conf import settings
import requests
import json




def GoogleCalendarInitView(request):
    return render(request,'login.html')

@csrf_exempt
def GoogleCalendarRedirectView(request):
    id_token = request.POST.get('credential')
    print(requests.post('https://oauth2.googleapis.com/tokeninfo',
                             data={'id_token': id_token}).json())
    response = requests.post('https://oauth2.googleapis.com/tokeninfo',
                             data={'id_token': id_token})

    if response.status_code != 200:
        return HttpResponse('Cannot authorize')
    data = response.json()
    email = data['email']
    client_id = data['aud']
    client_data = json.load(open(os.path.join(settings.BASE_DIR,'templates\\Gclient.json'),'r'))
    response = requests.post('https://oauth2.googleapis.com/token',
                              data={
                                 'code': id_token,
                                 'client_id': client_data['client_id'],
                                 'client_secret': client_data['client_secret'],
                                 'redirect_uri': '/rest/v1/calendar/redirect/',
                                 'grant_type': 'authorization_code',
                             })
    access_token = response.json()['access_token']
    print(response.json())
    service = build('calendar', 'v3', credentials=access_token)
    calendar = service.calendars().get(calendarId='primary').execute()
    print(calendar)
    events = service.events().list(calendarId=calendar['id'], timeMin=datetime.datetime.utcnow().isoformat() + 'Z',
                                   maxResults=10, singleEvents=True, orderBy='startTime').execute()
    
    return render(request, 'calendar_events.html', {'events': events})
  
   
