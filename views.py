import os
from django.shortcuts import redirect
from django.views import View
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from django.http import HttpResponse, JsonResponse

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class GoogleCalendarInitView(View):
    def get(self, request):
        # created a flow instance to manage the oAuth 2.0 Authorization Grant Flow steps
        flow = InstalledAppFlow.from_client_secrets_file('client_secret_last.json', scopes=SCOPES)

        #if this value doesnt match with an authorized URI, we get an "redirect_uri_mismatch" error
        flow.redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect'
        authorization_url, state = flow.authorization_url(access_type='offline',include_granted_scopes='true')
        request.session['state'] = state
        return redirect(authorization_url)

class GoogleCalendarRedirectView(View):
    def get(self, request):
        state = request.session.get('state')
        flow = InstalledAppFlow.from_client_secrets_file('client_secret_last.json', scopes=SCOPES, state=state)
        flow.redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect'

        # fetching OAuth 2.0 tokens
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        #Storing the credentials in the session
        credentials = flow.credentials

        request.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        service = build('calendar', 'v3', credentials=credentials)

        # Calling the calendar API
        events_result = service.events().list(calendarId='primary').execute()
        events = events_result.get('items', [])


        return JsonResponse({'status': 'success', 
                             'message': 'Events have been fetched',
                             'data': events
                        })