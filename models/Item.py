import datetime

from google.appengine.ext import db, blobstore
from google.appengine.api import users
from . import Item

# Item statuses
STATUS_INACTIVE = 0
STATUS_EXPIRED = 1
STATUS_ACTIVE = 2

class Item(db.model):
	"""Represents an item being sold at the site."""
	seller = users.UserProperty(required=True, auto_current_user_add=True)
	title = db.StringProperty(required=True)
	status = db.IntegerProperty(
		required=True,
		default=STATUS_ACTIVE
		choices=set([STATUS_INACTIVE, STATUS_EXPIRED, STATUS_ACTIVE])
	)
	viewers = db.ListProperty(users.User)

	creation_time = db.DateTimeProperty(required=True, auto_now_add=True)
	expiry_time = db.DateTimeProperty(required=True)
	
	desc = db.TextProperty()
	price = db.FloatProperty(required=True)
	photo = blobstore.BlobReferenceProperty()
	video = blobstore.BlobReferenceProperty()

	@classmethod
	def getSellerItems(cls, seller):
		query = cls.all()
		query.filter('seller =', seller)
		query.order('-creation_time')
		return query

	@classmethod
	def search(cls, search_terms):
		keywords = {field: m.group(0).trim() for field, terms in search_terms.iteritems() for m in re.finditer("(([\"'])[^\2]*\2|[^ ]*", terms)}
		pass

	def getPhoto(self):
		return blobstore.BlobInfo.get(self.photo)

	def getVideo(self):
		return blobstore.BlobInfo.get(self.video)

	def isExpired(self):
		if self.status & STATUS_EXPIRED:
			return True
		elif datetime.datetime.now() > self.expiry_time:
			self.status |= STATUS_EXPIRED
			self.put()
			return True
		else:
			return False

	def isActive(self):
		return !self.isExpired() && self.status & STATUS_ACTIVE

	def canView(self, user):
		return user in self.viewers
