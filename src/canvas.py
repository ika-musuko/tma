import dateutil.parser
import json
import event
import requests
import datetime
import dateutil.parser

'''
canvas.py

functions to interact with canvas and convert data into the model's representation
'''

def get_assignments(access_token: str="") -> 'list of DueEvent':
    '''
    gets the assignments from the courses and creates a list of DueEvents
    :param access_token: An access token, or API key, of the Canvas API
    :return: an unsorted list of DueEvents
    '''
    print("getting schedule from canvas...")
    today = datetime.datetime.today()
    canvas_url = "https://sjsu.instructure.com/api/v1/courses%s"
    headers = {
        "Authorization": ("Bearer %s" % (access_token)),
    }
    asnmt=list()
    print("making the request...")
    parsed_courses = json.loads(requests.get(canvas_url % ".json", headers=headers).text)
    for x in parsed_courses:
        if 'name' in x:
            a_course_url = canvas_url % ("/" + str(x['id']) + "/assignments.json")
            parsed_c_asnmt = json.loads(requests.get(a_course_url, headers=headers).text)
            for y in parsed_c_asnmt:
                due_at = y['due_at']
                if due_at is not None and y['has_submitted_submissions'] == False:
                    due_at = dateutil.parser.parse(y['due_at'], ignoretz=True)
                    if due_at >= today:
                        asnmt.append(event.DueEvent(due=due_at, name=y['name'], desc=y['description']))
                else:
                    asnmt.append(event.TaskEvent(name=y['name'], desc=y['description']))
    print("all done...! : )")
    return asnmt