import json

with open("1244638.json","r") as f:
		schedule = f.read().strip("[]").split(",")
		
for sc in schedule:
	print(sc)
	s = json.loads(sc)
	print("%s - due: %s, %s" % (s["name"], s["due_at"], ("submitted" if s["has_submitted_submissions"] else "not submitted")))