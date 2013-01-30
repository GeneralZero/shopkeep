import datetime

from google.appengine.ext import db, blobstore
from google.appengine.api import users, search
from google.appengine.api.search.SortExpression import ASCENDING, DESCENDING

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
		default=STATUS_ACTIVE,
		choices=set([STATUS_INACTIVE, STATUS_EXPIRED, STATUS_ACTIVE])
	)
	viewers = db.ListProperty(users.User)
	doc_id = db.StringProperty()

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
	def search(cls, search_terms, cursor, sortby=[], offset=0, limit=50):
		def getItemDocumentPair(doc):
			item = Item.get_by_id(doc.id)
			return (item, doc)

		expressions = []
		for field, order in sortby:
			expressions.append(search.SortExpression(
				expression=field,
				direction=order,
				default_value=''
			))
		sort_options = search.SortOptions(expressions=expressions, limit=1000)

		query_options = search.QueryOptions(
			limit=limit,
			cursor=cursor,
			offset=offset,
			sort_options=sort_options
		)

		try:
			query = search.Query(query_string=search_terms, options=query_options)
			results = search.Index(name='Item').search(query)
		except search.Error:
			logging.exception('Search failed')
			return ()
		else:
			return itertools.imap(getItemDocumentPair, results)

	def put(self, *args, **kwargs):
		doc = None

		try:
			index = search.Index(name='Item').get_range(
				start_id=self.doc_id,
				limit=1,
				include_start_object=True
			)
		except search.InvalidRequest:
			pass
		else:
			doc = response.results[0]

		fields = {
			'id': search.AtomField(name='id', value=self.key().id()),
			'status': search.AtomField(name='status', value=self.status),
			'title': search.TextField(name='title', value=self.title),
			'desc': search.HtmlField(name='desc', value=self.desc),
			'price': search.NumberField(name='price', value=self.price),
			'creation_time': search.DateField(name='creation_time', value=self.creation_time),
			'expiry_time': search.DateField(name='expiry_time', value=self.expiry_time)
		}

		if doc is None:
			doc = search.Document(fields=fields.values())
		else:
			for i, field in enumerate(doc.fields):
				if field.value != fields[field.name].value:
					doc.fields[i] = fields[field.name]

		try:
			search.Index(name='Item').put(doc)
		except search.Error:
			logging.exception('Adding item to search index failed.')
			return False
		else:
			self.doc_id = doc.doc_id
			super(Item, self).put(*args, **kwargs)
			return True

	def delete(self, *args, **kwargs):
		try:
			index = search.Index(name='Item').get_range(
				start_id=self.doc_id,
				limit=1,
				include_start_object=True
			)
		except search.InvalidRequest:
			pass
		else:
			doc = response.results[0]
			search.Index(name='Item').remove([doc.doc_id])
		finally:
			super(Item, self).delete(*args, **kwargs)

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
		return not self.isExpired() and self.status & STATUS_ACTIVE

	def canView(self, user):
		return user in self.viewers
