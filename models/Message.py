from google.appengine.ext import db
from google.appengine.ext import users
from . import Item

class Message(db.Model):
	"""represents a message thread between users"""
	thread_id = db.IntegerProperty(required=True)
	sender = db.UserProperty(required=True)
	recipient = db.UserProperty(required=True)
	datetime = db.DateTimeProperty(required=True, auto_now_add=True)
	content = db.TextProperty(required=True)
	item = db.ReferenceProperty(Item)

	
