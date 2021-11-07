import os
import cv2
import uuid #for generation of client id
import codecs
import hashlib
import smtplib
from Crypto.Cipher import AES
from django.db.models import Q
from .models import Document as doc
from django.shortcuts import render
from reportlab.pdfgen import canvas
from django.contrib import messages
from email.message import EmailMessage
from .models import LoginDetails,History, Check
from PyPDF2 import PdfFileReader,PdfFileWriter
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from .forms import LoginDetailsForm, ChangepwdForm, DocumentForm


def logout(request):
	try:
		del request.session['username']
	except:
		pass
	return HttpResponseRedirect("/")

def login_form(request):
	if request.method == 'POST':
		#form = LoginDetailsForm(request.GET)
		if True:
			username = request.POST.get('username')
			password = request.POST.get('password')

			try:
				q = LoginDetails.objects.get(username=username)
				if(q.password == password):
					request.session['username'] = username
					request.session['access'] = q.designation
					request.session['colourcode'] = q.colourcode
					if q.designation != 5:
						return HttpResponseRedirect("/userhome/")
					else:
						return HttpResponseRedirect("/detectorhome/")

				else:
					messages.error(request,"Invalid crediantials")
					return render(request,"index.html")
			except:
				messages.error(request,"Server down")
				return render(request,"index.html")
	#else:
		#form = LoginDetailsForm()
	return render(request, 'index.html')

k=[]
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userhome(request):
	try:
		username = request.session['username']
		designation = request.session['access']
		clientid = request.session['colourcode']
		levels = ['public','private','confidential','topsecret']
		context = {
		'username' : username,
		'designation' : levels[designation%4 - 1],
		'nbar' : 'home',
		}
	except:
		#return HttpResponse("vhvjh")
		return HttpResponseRedirect('/')
	if designation == 5:
		del request.session['username']
		return HttpResponseRedirect('/')
	return render(request, 'userHome.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detectorhome(request):
	try:
		username = request.session['username']
		designation = request.session['access']
		colourcode = request.session['colourcode']
		context = {
		'username' : username,
		'nbar' : 'home',
		}
	except:
		return HttpResponseRedirect('/')
	if designation != 5:
		del request.session['username'] #end the session
		return HttpResponseRedirect('/') #redirect to login page	
	return render(request, 'detectorHome.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def changepassword(request):
	try:
		username = request.session['username']
		designation = request.session['access']
		colourcode = request.session['colourcode']
	except:
		return HttpResponseRedirect('/')
	levels = ['public','private','confidential','topsecret']	
	if request.method == 'POST':
		form = ChangepwdForm(request.POST)
		if form.is_valid():
			current = form.cleaned_data['current']
			new = form.cleaned_data['new']
			reenter = form.cleaned_data['reenter']

			q = LoginDetails.objects.get(colourcode=int(colourcode))
			if q.password == current:
				if new == reenter:
					q.password = new
					q.save()
				else:
					return HttpResponse("new and reentered password doesn't match")
			else:
				return HttpResponse("incorrect password")
	else:
		form = ChangepwdForm()

	context = {
		'form' : form,
		'username' : username,
		'designation' : levels[designation%4 -1],
		'nbar' : 'changepass'
	}
	if designation == 5:
		return render(request, 'detector_changePassword.html', context)
	else:
		return render(request, 'user_changePassword.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def modelformupload(request):
	try:
		username = request.session['username']
		designation = request.session['access']
		colourcode = request.session['colourcode']
	except:
		return HttpResponseRedirect('/')
	if request.method == 'POST':
		form = DocumentForm(request.POST, request.FILES)
		if form.is_valid():
			if request.POST['accesslevel'] > str(designation):
				return HttpResponse("Access level not allowed")
			else:
				form.save()
				q = doc.objects.last()
				q.author = username
				q.uploadlevel = designation
				name = q.document.name
				level = q.accesslevel
				print(name)
				q.save()
				modifypdf(name, level)

			return HttpResponseRedirect('/userhome')
	else:
		form = DocumentForm()
	levels = ['public', 'private', 'confidential', 'topsecret']
	context = {
		'form' : form,
		'designation': levels[designation%4 -1],
		'nbar':'uploaddoc',
		'username' : username,
	}
	if designation == 5:
		del request.session['username']
		return HttpResponseRedirect('/')
	return render(request, 'user_uploadDocument.html', context)

def modifypdf(name,level):
	pdf1File = open('./media/'+name, 'rb')
	pdf1Reader = PdfFileReader(pdf1File)
	l=[]
	l=name.split('/')
	l=l[-1]
	for i in range(int(level),5):
		pdf2File = open('./media/documents/{}.pdf'.format(i),'rb')
		pdf2Reader = PdfFileReader(pdf2File)
		pdfWriter = PdfFileWriter()
		for pageNum in range(pdf1Reader.numPages):
			pageObj = pdf1Reader.getPage(pageNum)
			pdfWriter.addPage(pageObj)
		for pageNum in range(pdf2Reader.numPages):
			pageObj = pdf2Reader.getPage(pageNum)
			pdfWriter.addPage(pageObj)
		pdfOutputFile = open('./media/documents/{}_{}.pdf'.format(l[:-4],i), 'wb')
		pdfWriter.write(pdfOutputFile)
		pdfOutputFile.close()
		pdf2File.close()
	pdf1File.close()

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def checkdocument(request):
    try:
        username = request.session['username']
        designation = request.session['access']
    except:
        return HttpResponseRedirect('/')
    if designation != 5:
        del request.session['username']  # end the session
        return HttpResponseRedirect('/')  # redirect to login page
    if request.method=='POST':
        file = request.FILES['myfile']
        abc = Check()
        abc.file = file
        abc.save()
        q = Check.objects.last()
        name = q.file.name
        p = checker(name)
        if p==0:
        	messages.success(request, 'No leak detected')
        elif p==1:
        	messages.error(request, 'bhavesh leaked')
        elif p==2:
        	messages.error(request, 'shivam leaked')
        elif p==3:
        	messages.error(request, 'mehul leaked')
        else:
        	messages.error(request, 'goyal leaked')
        q.delete()

    context = {
        'username': username,
        'nbar': 'checkdoc',
    }
    return render(request, "detector_checkDocument.html", context)

def checker(name):
	pdfFileObj = open('./media/'+name, 'rb')
	pdfReader = PdfFileReader(pdfFileObj)
	pageObj = pdfReader.getPage(pdfReader.numPages-1)
	q=pageObj.extractText()
	pdfFileObj.close()
	for i in range(1,5):
		p = open('./media/documents/{}.pdf'.format(i),'rb')
		p1 = PdfFileReader(p)
		p2 = p1.getPage(0).extractText()
		if p2 in q:
			return i
	else:
		return 0

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def displayfiles(request):
	try:
		username = request.session['username']
		clientid = request.session['colourcode']
		designation = request.session['access']
	except:
		return HttpResponseRedirect('/')
	q = doc.objects.filter(accesslevel__lte=designation)
	levels = ['public', 'private', 'confidential', 'topsecret']
	context = {
		'data': q,
		'nbar': 'displaydoc',
		'designation': levels[designation%4 -1],
		'username': username,
	}
	
	if request.method == 'POST':
		if request.POST.get('filename'): #filename is name attribute of the button clicked in template
			name = request.POST.get('filename')
			name1 = name[:-4]+"_"+str(designation)+".pdf"
			out = "documents/document-output.pdf"
			val = "success"
			if val == "success":
				a= History(username=username,filename=name,status="Viewed the file")
				a.save()
				return HttpResponseRedirect("/media/" + name1)
			else:
				return HttpResponse("Embed failure")
	if designation == 5:
		del request.session['username']
		return HttpResponseRedirect('/')
	return render(request, "user_searchDocument.html", context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def history(request):
	try:
		username = request.session['username']
		designation = request.session['access']
	except:
		return HttpResponseRedirect('/')
	if designation != 5:
		del request.session['username']  # end the session
		return HttpResponseRedirect('/')  # redirect to login page

	#q = DetectorUpload.objects.exclude(status='Not Viewed').order_by("-uploaded_at")
	q = History.objects.all()
	context = {
		'nbar': 'history',
		'data': q,
		'designation': designation,
		'username': username,
	}

	return render(request, 'detector_history.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def deletefile(request):
	try:
		username = request.session['username']
		colourcode = request.session['colourcode']
		designation = request.session['access']
	except:
		return HttpResponseRedirect('/')
	q = doc.objects.filter(accesslevel__lte=designation) #make it author
	levels = ['public', 'private', 'confidential', 'topsecret']
	context = {
		'data': q,
		'nbar': 'deletedoc',
		'designation': levels[designation%4 -1],
		'username': username,
	}
	#print (type(designation))
	
	document_location = "/media/"
	if request.method == 'POST':
		if request.POST.get('filename'): #filename is name attribute of the button clicked in template
			name = request.POST.get('filename')
			del_location = document_location + name
			print(del_location)
			delfile = doc.objects.get(document=name)
			if(designation<int(delfile.uploadlevel) ):
				k.append(username)
				messages.success(request, 'File deleted successfully ')
				# return render(request, 'user_deleteDocument.html',context)
				a= History(username=username,filename=name,status="Tried to delete")
				a.save()
				to=['27goyalbhavesh@gmail.com']
				b = username + " tried to delete document "+name 
				email_id='bhavstar99'
				email_pass='dllttscwyukizvxq'
				msg=EmailMessage()
				msg['Subject']='Data Leakage Detected'
				msg['From']=email_id
				msg['To']= to[0]
				con = username+ " tried to delete the document "+ name
				msg.set_content(con)
				with smtplib.SMTP_SSL('smtp.gmail.com',465)as smtp:
					print("vhjvbj")
					smtp.login(email_id,email_pass)
					smtp.send_message(msg)
					smtp.quit()
					print("d")
				return render(request,"userHome.html")
			else:
				doc.objects.get(document=name).delete()
				messages.success(request, 'File deleted ')
				os.remove("./media/"+name)
				return render(request,"userHome.html")
			#doc.objects.get(document=name).delete()
			#subprocess.call(["rm", del_location])

	if designation == 5:
		del request.session['username']
		return HttpResponseRedirect('/')
	return render(request, 'user_deleteDocument.html',context)
