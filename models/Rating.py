from google.appengine.ext import db
from google.appengine.api import users
from . import Item

class Rating(db.Model):
	"""Represents a user's rating of a seller or item and the
	associated comments"""
	seller = users.UserProperty(required=True)
	rater = users.UserProperty(required=True)
	item = db.ReferenceProperty(Item, required=True)
	rating = db.RatingProperty(required=True)
	comments = db.TextProperty()

	@classmethod
	def getRatings(cls, item):
		q = cls.all()
		q.filter('item =', item)
		return q
