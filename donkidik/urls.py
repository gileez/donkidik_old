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
    # ===== ADMIN ======
    url(r'^admin/', admin.site.urls),
    # ===== VIEWS ======
    url(r'^$', views.home),
    url(r'^login/$', views.index),
    url(r'^posts/$', views.posts),
    # ===== API ========
    url(r'^api/signup/$', api.signup),
    url(r'^api/login/$', api.login_req),
    url(r'^api/logout/$', api.logout_req),
    url(r'api/post/add/$', api.create_post),
    url(r'api/posts/(?P<uid>[0-9]+)/$', api.user_posts),
    url(r'api/posts/all/$', api.get_posts),
    url(r'api/post/types/$', api.get_post_types),
    url(r'api/spots/get/$', api.get_spots),
    # follow
    url(r'api/user/(?P<uid>[0-9]+)/follow/$', api.follow),
    # unfollow
    url(r'api/user/(?P<uid>[0-9]+)/unfollow/$', api.unfollow),

]
