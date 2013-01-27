from google.appengine.ext import db
from google.appengine.api import users

class User(db.Model):
	"""Represents a user's rating of a seller or item and the
	associated comments"""
	id = db.IntegerProperty(required=True)
	email = db.Email(required=True)
	first_name = db.StringProperty(required=True)
	last_name = db.StringProperty(required=True)
	address = db.PostalAddress()
	phone_number = db.PhoneNumber()
	registered = db.DateTimeProperty(auto_now_add=True)
	last_loggedin = db.DateTimeProperty(auto_now_add=True)
	#last_IP = db.IntegerProperty()
	info = db.TextProperty()
	photo = db.blobstore.BlobReferenceProperty()
	video = db.blobstore.BlobReferenceProperty()
