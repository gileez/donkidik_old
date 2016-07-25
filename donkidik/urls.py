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
    url(r'^login/$', views.index), #login
    url(r'^posts/$', views.posts), #all posts
    # TODO view user profile
    #url(r'^user/(?P<uid>[0-9]+)/$', views.userProfile),
    # TODO edit user profile
    #url(r'^user/profile/$', views.userProfile),
    # TODO specific spot
    #url(r'^spot/(?P<sp_id>[0-9]+)/$', views.userProfile),
    # TODO session
    #url(r'^session/(?P<se_id>[0-9]+)$', views.session),
    # TODO all sessions
    #url(r'^session/$', views.session),
# ===== API ========
    # signup
    url(r'^api/signup/$', api.signup),
    # login
    url(r'^api/login/$', api.login_req),
    # logout
    url(r'^api/logout/$', api.logout_req),
    # add post
    url(r'api/post/add/$', api.create_post),
    # remove post
    url(r'api/post/remove/(?P<uid>[0-9]+)/$', api.remove_post),
    # update post
    url(r'api/post/update/(?P<uid>[0-9]+)/$', api.update_post),
    # specific user posts
    url(r'api/posts/(?P<uid>[0-9]+)/$', api.user_posts),
    # all posts
    url(r'api/posts/all/$', api.get_posts),
    # get post types: returns a json of post types
    url(r'api/post/types/$', api.get_post_types),
    # get spots: returns a json of all possible spots
    url(r'api/spots/get/$', api.get_spots),
    # follow
    url(r'api/user/(?P<uid>[0-9]+)/follow/$', api.follow),
    # unfollow
    url(r'api/user/(?P<uid>[0-9]+)/unfollow/$', api.unfollow),
    # up vote
    url(r'api/posts/(?P<pid>[0-9]+)/up/$', api.post_upvote),
    # down vote
    url(r'api/posts/(?P<pid>[0-9]+)/up/$', api.post_down_vote),
    # TODO add forcast
    url(r'api/forecast/add/$', api.create_forecast),
    # TODO remove forecast
    url(r'api/forecast/remove/(?P<pid>[0-9]+)/$', api.remove_forecast),
    # TODO update forcast
    url(r'api/forecast/update/(?P<pid>[0-9]+)/$', api.update_forecast),
    # TODO add session
    url(r'api/session/add/$', api.create_session),
    # TODO join session
    url(r'api/session/join/$', api.join_session),
    # TODO leave session
    url(r'api/session/leave/$', api.leave_session),
    # TODO add comment
    url(r'api/post/(?P<pid>[0-9]+)/add_comment/$', api.add_comment),
    # TODO remove comment
    url(r'api/post/(?P<pid>[0-9]+)/rem_comment/$', api.rem_comment),
    # TODO update comment
    url(r'api/post/(?P<pid>[0-9]+)/update_comment/$', api.update_comment),


]
