import bottle

# create page at /hello
@bottle.route("/hello")
def hello():
	return "what is this"

# create subpage of hello and use a template for content with bottle.template
@bottle.route("/")
@bottle.route("/hello/<name>")
def greet(name="XXXX"):
	return bottle.template('hello {{name}}, how are you?', name=name)

	
# filter pages
@bottle.route("/object")
def object():
	return "is this an int"
	
# will only create a page if  id is an int
@bottle.route("/object/<id:int>")
def callback(id):
	assert isinstance(id, int)
	
@bottle.route("/show")
def show():
	return "is this a name"

# will only create a page if isalpha() returns true	
@bottle.route("/show/<name:re:[a-z]+>")
def callback(name):
	assert name.isalpha()
	
	

bottle.run(host='localhost', port=8080, debug=True)