import requests
import json

CANVAS = "https://sjsu.instructure.com/api/v1/%s"
ACCESS_TOKEN = "12~euEvlRyP4Jssa5G6xmq8ke1hp9GC9YtHZUEKM7LOC2hCwWbmfDCYb7yGaDbILYlO"

headers = {
	"Authorization": ("Bearer %s" % (ACCESS_TOKEN)),
}

thing_url = CANVAS % ("")
thing = requests.get(thing_url, headers=headers)