from google.appengine.ext import db
from google.appengine.api import users
from . import Item

TYPE_WISHLIST = 0
TYPE_SHOP = 1
TYPE_COLLECTION = 2

class Collection(db.model):
	"""Represents a private or public collection of items."""
	type = db.IntegerProperty(required=True, choices=set([TYPE_WISHLIST, TYPE_SHOP, TYPE_COLLECTION])
	owners = db.ListProperty(users.User, required=True)
	items = db.ListProperty(db.Key)
	query = db.ListProperty(str)

	def getItems(self):
		if query:
			return Item.search(self.query)
		else:
			return Item.get(self.items)
