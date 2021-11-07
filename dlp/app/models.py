from django.db import models
from django.utils import timezone


class LoginDetails(models.Model):
	username = models.CharField(max_length=50)
	password = models.CharField(max_length=50)
	designation = models.IntegerField(default=1)
	colourcode = models.AutoField(primary_key = True)
	clientid = models.CharField(max_length=17, default="xyz")
	cipher_text = models.CharField(max_length=25, default="xyz")
	hash_text = models.CharField(max_length=65, default="xyz")

	def __str__(self):
		return self.username

class Document(models.Model):
	title = models.CharField(max_length=50,default='null')
	author = models.CharField(max_length=50, default='null')
	description = models.CharField(max_length=500, blank=True)
	accesslevel = models.CharField(max_length=50, default=4)
	uploadlevel = models.CharField(max_length=50, default=5)
	document = models.FileField(upload_to='documents/')
	uploaded_at = models.DateTimeField(default=timezone.now())

	def __str__(self):
		return self.title

class History(models.Model):
	username = models.CharField(max_length=50)
	leakdetetcetedat = models.DateTimeField(default=timezone.now())
	filename = models.CharField(max_length=100)
	status = models.CharField(max_length=20, default="Not Viewed")

	def __str__(self):
		return self.username+" "+self.filename+" "+self.status+" "+str(self.leakdetetcetedat)

class Check(models.Model):
	file = models.FileField(upload_to='check/')
	