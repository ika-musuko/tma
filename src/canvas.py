import dateutil.parser
import json
import event
import requests
import datetime
from bs4 import BeautifulSoup
'''
canvas.py

functions to interact with canvas and convert data into the model's representation
'''

canvas_url = "https://sjsu.instructure.com/api/v1%s"


def get_assignments(access_token: str="") -> 'list of Event':
    '''
    gets the assignments from the courses and creates a list of Events
    relies on get_courses() and get_headers()
    :param access_token: An access token, or API key, of the Canvas API
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
                                                                    + "?include[]=observed_users")
        parsed_c_asnmt = json.loads(requests.get(a_course_url, headers=get_headers(access_token)).text)
        for y in parsed_c_asnmt:
            due_at = y['due_at']
            desc=y['description']
            if desc is not None:
                desc=remove_tags(desc)
            if due_at is not None and y['has_submitted_submissions'] == False:
                due_at = dateutil.parser.parse(y['due_at'], ignoretz=True)
                if due_at >= today:
                    asnmt.append(event.DueEvent(due=due_at, name=y['name'], desc=desc))
            else:
                asnmt.append(event.TaskEvent(name=y['name'], desc=desc))
    print("all done...! : )")
    return asnmt


def get_courses(access_token: str=""):
    '''
    :param access_token: An access token, or API key, of the Canvas API
    :return: a list of dictionaries, with 'id' and 'name' fields
    '''
    course_list = list()
    parsed_courses = json.loads(requests.get(canvas_url % "/courses", headers=get_headers(access_token)).text)
    for x in parsed_courses:
        if 'name' in x:
            crs = {'id' : str(x['id']), 'name' : x['name']}
            course_list.append(crs)
    return course_list


def get_headers(access_token: str=""):
    headers = {
        "Authorization": ("Bearer %s" % access_token),
    }
    return headers


def remove_tags(text):
    return BeautifulSoup(text, "html.parser").get_text()
