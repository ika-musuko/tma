import requests
import json
'''
I don't know how to split this up among the modules
But this should work

This code finds the course ids taken by Steven
and for each course id finds assignments
which may not be all the assignments?? for some reason??
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
        for x in parsed_c_asnmt:
            print(x)
        asnmt.append(parsed_c_asnmt)