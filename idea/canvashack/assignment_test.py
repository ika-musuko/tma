import json

with open("1244638.json","r") as f:
		schedule_s = f.read()

schedule = json.loads(schedule_s)

for s in schedule:
	print("%s - due: %s, %s" % (s["name"], s["due_at"], ("submitted" if s["has_submitted_submissions"] else "not submitted")))