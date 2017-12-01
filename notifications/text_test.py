from textmagic.rest import TextmagicRestClient

username = 'lucychibukhchyan'
api_key = 'sjbEMjfNrrglXY4zCFufIw9IPlZ3SA'
client = TextmagicRestClient(username, api_key)

message = client.message.create(phones="7206337812", text="wow i sent a text from python!!!!")
