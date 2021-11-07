from django import forms
from .models import Document, LoginDetails

class ChangepwdForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(ChangepwdForm, self).__init__(*args, **kwargs)
		self.fields['current'].widget.attrs = {
			'class' : 'form-control',
			'placeholder' : 'Current Password'
		}
		self.fields['new'].widget.attrs = {
			'class' : 'form-control',
			'placeholder' : 'New Password'
		}
		self.fields['reenter'].widget.attrs = {
			'class' : 'form-control',
			'placeholder' : 'Re-enter Password'
		}

	current = forms.CharField(max_length=50, widget=forms.PasswordInput)
	new = forms.CharField(max_length=50, widget=forms.PasswordInput)	
	reenter = forms.CharField(max_length=50, widget=forms.PasswordInput)

class DocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'title'
        }
        self.fields['description'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'description'
        }
        self.fields['accesslevel'].widget.attrs = {
            'class': 'form-control',
            'placeholder': 'accesslevel',
        }
    title = forms.CharField(max_length=50)
    description = forms.CharField(max_length=500)
    accesslevel = forms.CharField(max_length=50)
    document = forms.FileField()

    class Meta:
        model = Document
        fields = ('title','description', 'accesslevel', 'document')

class MyModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MyModelForm, self).__init__(*args, **kwargs)
        # self.fields['username'].widget.attrs = {
        #     'class': 'form-control',
        #     'placeholder':'username',
        # }
        self.fields['password'].widget.attrs = {
            'class': 'form-control',
            'placeholder':'password',
        }  
        self.fields['username'].widget.attrs = {
            'class': 'form-control',
            'placeholder':'username',
        }   
    password = forms.CharField(widget=forms.PasswordInput,max_length=50)
    username = forms.CharField(max_length=50)
    class Meta:
        model = LoginDetails
        fields = ('username', 'password')
        
class LoginDetailsForm(MyModelForm):
    form_class = MyModelForm

    title = forms.CharField(max_length=50)
    description = forms.CharField(max_length=500)
    accesslevel = forms.CharField(max_length=50)
    document = forms.FileField()

    class Meta:
        model = Document
        fields = ('title','description', 'accesslevel', 'document')