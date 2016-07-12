from donkidik import views,api
"""donkidik URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home),
    url(r'^login/$', views.index),
    url(r'^posts/$', views.posts),
    url(r'^api/signup/$', api.signup),
    url(r'^api/login/$', api.login_req),
    url(r'^api/logout/$', api.logout_req),
    url(r'^gal/1/$', views.gal1),
    url(r'^gal/2/$', views.gal2),
    url(r'^gal/3/$', views.gal3)
]
