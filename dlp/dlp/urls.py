"""dlp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from app import views


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', views.login_form),
    url(r'^logout', views.logout, name='logout'),
    url(r'^userhome', views.userhome),
    url(r'^detectorhome', views.detectorhome),
    url(r'^changepassword', views.changepassword),
    url(r'^upload', views.modelformupload),
    url(r'^displayfiles', views.displayfiles),
    url(r'^checkdocument', views.checkdocument),
    url(r'^history', views.history),
    url(r'^deletefile', views.deletefile),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)