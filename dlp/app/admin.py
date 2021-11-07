from django.contrib import admin
from .models import LoginDetails, Document, History, Check
# Register your models here.

admin.site.register(LoginDetails)
admin.site.register(Document)
admin.site.register(History)
admin.site.register(Check)