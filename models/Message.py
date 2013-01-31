import datetime
import hashlib
from os import urandom
from google.appengine.ext import db
from google.appengine.ext import users
from . import Item

class Message(db.Model):
	"""represents a message thread between users"""
	thread_id = db.StringProperty(required=True)
	sender = users.UserProperty(required=True, auto_current_user_add=True)
	recipient = users.UserProperty(required=True)
	datetime = db.DateTimeProperty(required=True, auto_now_add=True)
	content = db.TextProperty(required=True)
	item = db.ReferenceProperty(Item)
	read = db.BooleanProperty(required=True)

	@classmethod
	def getMessages(cls, user):
		q = cls.all()
		q.filter('recipient = ', user)
		q.order('datetime');
		return q

	@classmethod
	def replyToMessage(cls, message, content):
		x = Message()
		x.thread_id = message.thread_id
		x.recipient = message.sender
		x.content = content
		x.item = message.item
		x.read = False
		x.put()

	@classmethod
	def createMessage(cls, recipient, item, content):
		x = Message()
		randomSalt = urandom()
		h = hashlib.sha512()
		# using hash of sender, recipient, datetime, and random salt to create thread_id
		tid_hash_object = h.update(str(datetime.datetime.now.date)+str(recipient)+str(users.get_current_user())+str(randomSalt))
		x.thread_id = tid_hash_object.hexdigest()
		x.recipient = recipient
		x.content = content
		x.item = item
		x.read = False
		x.put()

	@classmethod
	def getThread(cls, id):
		q = cls.all()
		q.filter('thread_id = ', id)
		q.order('datetime')
		return q


