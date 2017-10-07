import requests
import json

CANVAS = "https://sjsu.instructure.com/api/v1/%s"
ACCESS_TOKEN = "12~euEvlRyP4Jssa5G6xmq8ke1hp9GC9YtHZUEKM7LOC2hCwWbmfDCYb7yGaDbILYlO"

headers = {
	"Authorization": ("Bearer %s" % (ACCESS_TOKEN)),
}

courses_url = CANVAS % ("courses")
courses = requests.get(courses_url, headers=headers)
courses_json = courses.json()
for c in courses_json:
	with open("%s.calendar" % (c['id']), 'w') as f:
		c_url

'''calendar_url = CANVAS % ("courses.json")
calendar = requests.get(calendar_url, headers=headers)
print(calendar.text)'''