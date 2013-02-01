import datetime
import operator
from Crypto.Hash import SHA256
from Crypto import Random
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
	def getMessages(cls, user, inbox=True, sent=True):
		def orderedGenerator(queries, field, dir):
			objs = []
			# Get first item from each query
			for query in queries.enumerate():
				try:
					objs.append(query.next())
				except StopIteration:
					# Remove empty queries
					queries.remove(query)

			dir = True if dir == 'DESC' else False
			while filter(None, objs):
				obj = min(objs, key=operator.attrgetter(field), reverse=dir)
				index = objs.index(obj)
				try:
					objs[index] = queries[index].next()
				except StopIteration:
					# Query exhausted, remove it from list
					queries.remove(index)
					objs.remove(index)
				yield obj

		queries = []
		if inbox:
			q = cls.all()
			q.filter('recipient = ', user)
			q.order('datetime')
			queries.append(q)
		if sent:
			q = cls.all()
			q.filter('sender = ', user)
			q.order('datetime')
			queries.append(q)

		return orderedGenerator(queries, 'datetime', 'DESC')

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
		# not 100% sure about correct PyCrypto Random usage
		randomSalt = int( Random.new().read(32) )
		h = SHA256.new()
		# using hash of sender, recipient, datetime, and random salt to create thread_id
		h.update( str(datetime.datetime.now.date) )
		h.update( str(recipient) )
		h.update( str( users.get_current_user() ) )
		h.update( str(randomSalt) )
		x.thread_id = h.hexdigest()
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


