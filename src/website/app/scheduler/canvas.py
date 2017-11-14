import dateutil.parser
import json
from . import event
import requests
import datetime
from bs4 import BeautifulSoup
'''
canvas.py

functions to interact with canvas and convert data into the model's representation
'''

canvas_url = "https://sjsu.instructure.com/api/v1%s"

def get_assignments(access_token: str="", all_events: bool=False) -> 'list of DueEvent':
    '''
    gets the assignments from list of courses and creates a list of Events
    relies on get_courses() and get_headers()
    :param access_token: An access token, or API key, of the Canvas API
    :param all_events: flag to get events without a due date
    :return: an unsorted list of DueEvents
    '''
    print("getting schedule from canvas...")
    today = datetime.datetime.today()
    asnmt = list()
    print("making the request...")
    parsed_courses = get_courses(access_token)
    for x in parsed_courses:
        a_course_url = canvas_url % ("/courses/" + str(x['id']) + "/assignments"
                                                                + "?include[]=submission"
                                                                + "?include[]=assignment_visibility"
                                                                + "?include[]=all_dates"
                                                                + "?include[]=overrides"
                                                                + "?include[]=observed_users"
                                    )
        parsed_c_asnmt = json.loads(requests.get(a_course_url, headers=get_headers(access_token)).text)
        for y in parsed_c_asnmt:
            # hack fix for not loading transfer orientation plus (todo: actual course selector)
            if y['course_id'] == 1237818:
                continue
            due_at = convert_timestr(y['due_at'])
            desc = remove_tags(y['description'])
            if due_at is not None and due_at >= today:
                asnmt.append(event.DueEvent(due=due_at, name=y['name'], desc=desc))
            elif all_events:
                asnmt.append(event.TaskEvent(name=y['name'], desc=desc))
    print("all done...! : )")
    return asnmt

def get_calendar_events(access_token: str="") -> 'list of Event':
    '''
    gets a list of calendar events from the calendar_events API endpoint
    doesn't work sometimes (???)
    :param access_token: An access token, or API key, of the Canvas API
    :return: a list of Events
    '''
    cal_evs = list()
    print("getting calendar events from canvas....")
    print("making request...")
    parsed_cal = json.loads(requests.get(canvas_url % "/calendar_events", headers=get_headers(access_token)).text)
    print("request result: ")
    #print(parsed_cal)
    for x in parsed_cal:
        desc = remove_tags(x['description'])
        cal_evs.append(event.Event(name=x['name']
                                    , desc=desc
                                    , start=convert_timestr(x['start_at'])
                                    , end=convert_timestr(x['end_at'])
                                  )
                      )
    print(cal_evs)
    return cal_evs


def get_courses(access_token: str="")-> 'list of dict':
    '''
    :param access_token: An access token, or API key, of the Canvas API
    :return: a list of dicts, with 'id' and 'name' fields
    '''
    course_list = list()
    parsed_courses = json.loads(requests.get(canvas_url % "/courses", headers=get_headers(access_token)).text)
    for x in parsed_courses:
        if 'name' in x:
            crs = {'id': str(x['id']), 'name': x['name']}
            course_list.append(crs)
    #print(course_list)
    return course_list


def get_headers(access_token: str=""):
    headers = {
        "Authorization": ("Bearer %s" % access_token),
    }
    return headers

def convert_timestr(timestr: None):
    if timestr is None:
        return timestr
    return dateutil.parser.parse(timestr, ignoretz=True)-datetime.timedelta(hours=7) # todo, implement actual timezone support instead of this hack

def remove_tags(text: None):
    if text is None:
        return text
    return BeautifulSoup(text, "html.parser").get_text()
