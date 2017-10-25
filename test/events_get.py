import sys
sys.path.append("../src")
import requests
import json
import util
import canvas
'''
I don't know how to split this up among the modules
But this should work

This code finds the course ids taken by Steven
and for each course id finds assignments
which may not be all the assignments?? for some reason??
'''

for x in canvas.get_from_canvas(access_token="12~ctFQBI3R4WVBmhQi2rV1PbTabRtXkCDwRjv1sM2ZHD5DXzoQBXlZL6NRn8ZXLx8e"):
    print(x)


'''
canvas_url =  "https://sjsu.instructure.com/api/v1/courses%s"
access_token = "12~ctFQBI3R4WVBmhQi2rV1PbTabRtXkCDwRjv1sM2ZHD5DXzoQBXlZL6NRn8ZXLx8e"

headers = {
	"Authorization": ("Bearer %s" % (access_token)),
}

courses_url = canvas_url % (".json")
print(courses_url)

courses = requests.get(courses_url, headers=headers)
courses_json = courses.text
parsed_courses = json.loads(courses_json)

asnmt = list()

for x in parsed_courses:
    if 'name' in x:
        a_course_url = canvas_url % ( "/" + str(x['id']) + "/assignments.json")
        c_asnmt = requests.get(a_course_url, headers=headers)
        c_asnmt_json = c_asnmt.text
        parsed_c_asnmt = json.loads(c_asnmt_json)
        print("Assignments for course id", str(x['id']), x['name'])
        for y in parsed_c_asnmt:
            print(y)
            asnmt.append(y)

print("asnmt:")
for x in asnmt:
    print(x)

# calendar events
calev = json.loads(requests.get("https://sjsu.instructure.com/api/v1/calendar_events", headers=headers).text)

print("calev:")
for x in calev:
    print(calev)
'''
