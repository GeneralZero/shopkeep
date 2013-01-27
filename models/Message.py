from google.appengine.ext import db
from google.appengine.ext import users
from . import Item

class Message(db.Model):
	"""represents a message thread between users"""
	thread_id = db.IntegerProperty(required=True)
	sender = users.UserProperty(required=True, auto_current_user_add=True)
	recipient = users.UserProperty(required=True)
	datetime = db.DateTimeProperty(required=True, auto_now_add=True)
	content = db.TextProperty(required=True)
	item = db.ReferenceProperty(Item)
	read = db.BooleanProperty(required=True)

	@classmethod
	def getMessages(cls, user):
		pass

	@classmethod
	def replyToMessage(message, content):
		pass

	@classmethod
	def createMessage(item, content):
		pass

	@classmethod
	def getThread(id):
		pass


