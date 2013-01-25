import logging
import pickle

from google.appengine.ext import db
from google.appengine.api import users
from . import Item, Collection

class Log(db.model):
	"""Represents entries in the audit log for administrative
	purposes"""
	datetime = db.DateTimeProperty(required=True, auto_now_add=True)
	performer = users.UserProperty(required=True, auto_current_user_add=True)
	changed_item = db.ReferenceProperty(Item)
	changed_user = db.UserProperty()
	changed_collection = db.ReferenceProperty(Collection)

	level = db.IntegerProperty(
		required=True,
		default=logging.INFO,
		choices=set([
			logging.DEBUG,
			logging.INFO,
			logging.WARNING,
			logging.ERROR,
			logging.CRITICAL
		])
	)

	message = db.TextProperty(required=True)
	debuginfo = db.BlobProperty()

class LogHandler(logging.Handler):
	"""Handles logging by putting it into the above Log table."""

	def createLock(self):
		"""Return None as a lock since the datastore is threadsafe."""
		return None

	def emit(self, record):
		"""Make a log entry and put it to the database."""
		entry = Log(level=record.levelno, message=record.message)
		if entry.__dict__.get('performer', False):
			entry.performer = record.performer

		if isinstance(entry.target, Item):
			entry.changed_item = record.target
		elif isinstance(entry.target, users.User):
			entry.changed_user = record.target
		elif isinstance(entry.target, Collection):
			entry.changed_collection = record.target
		else:
			raise ValueError('Invalid target type.')

		entry.debuginfo = pickle.dumps(record)
		entry.put()
